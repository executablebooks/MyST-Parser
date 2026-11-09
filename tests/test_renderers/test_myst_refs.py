import sys

import pytest
from docutils import nodes
from sphinx.util.console import strip_colors
from sphinx_pytest.plugin import CreateDoctree


@pytest.mark.parametrize(
    "test_name,text,should_warn",
    [
        ("null", "", False),
        pytest.param(
            "missing",
            "[](ref)",
            True,
            marks=pytest.mark.skipif(
                sys.platform == "win32",
                reason="Path separators differ on Windows",
            ),
        ),
        ("doc", "[](index)", False),
        ("doc_with_extension", "[](index.md)", False),
        ("doc_nested", "[*text*](index)", False),
        ("ref", "(ref)=\n# Title\n[](ref)", False),
        ("ref_nested", "(ref)=\n# Title\n[*text*](ref)", False),
        pytest.param(
            "duplicate",
            "(index)=\n# Title\n[](index)",
            True,
            marks=pytest.mark.skipif(
                sys.platform == "win32",
                reason="Path separators differ on Windows",
            ),
        ),
        ("ref_colon", "(ref:colon)=\n# Title\n[](ref:colon)", False),
        # a std-domain label id in the target doc resolves without warning
        ("doc_with_target_id", "(ref)=\n# Title\n[](index.md#ref)", False),
        # a label referenced by *name* resolves to its actual anchor id
        (
            "doc_with_target_name",
            "(ref:colon)=\n# Title\n[](index.md#ref:colon)",
            False,
        ),
    ],
)
def test_parse(
    test_name: str,
    text: str,
    should_warn: bool,
    sphinx_doctree: CreateDoctree,
    file_regression,
    normalize_doctree_xml,
):
    sphinx_doctree.set_conf({"extensions": ["myst_parser"], "show_warning_types": True})
    result = sphinx_doctree(text, "index.md")
    assert not result.warnings

    doctree = result.get_resolved_doctree("index")

    if should_warn:
        assert result.warnings
    else:
        assert not result.warnings

    doctree["source"] = "root/index.md"
    doctree.attributes.pop("translation_progress", None)
    outcome = normalize_doctree_xml(doctree.pformat())
    if result.warnings.strip():
        outcome += "\n\n" + strip_colors(result.warnings.strip())
    file_regression.check(outcome, basename=test_name, extension=".xml")


def test_project_resolution_beats_local_implicit(sphinx_doctree: CreateDoctree):
    """`[](#name)` prefers project-wide targets over local implicit names.

    Regression: a local implicit heading name (e.g. "Installation") must not
    hijack a link that previously resolved to another document's explicit
    target of the same name.
    """
    sphinx_doctree.set_conf(
        {"extensions": ["myst_parser"], "suppress_warnings": ["toc.not_included"]}
    )
    sphinx_doctree.srcdir.joinpath("other.md").write_text(
        "(installation)=\n\n# Other Install\n", encoding="utf8"
    )
    result = sphinx_doctree("# Installation\n\n[](#installation)\n", "index.md")
    doctree = result.get_resolved_doctree("index")
    from docutils import nodes as docutils_nodes

    ref = next(doctree.findall(docutils_nodes.reference))
    # project-wide resolution (std:ref) fills in the *target* section's
    # title and a refuri; the local fallback would set refid + local title
    assert ref.astext() == "Other Install", ref.attributes
    assert "refuri" in ref.attributes, ref.attributes
    assert not ref.get("refid"), ref.attributes


def test_local_implicit_fallback_beyond_anchor_depth(sphinx_doctree: CreateDoctree):
    """A heading beyond `heading_anchors` depth resolves locally, unwarned,
    when nothing project-wide matches."""
    sphinx_doctree.set_conf({"extensions": ["myst_parser"], "myst_heading_anchors": 1})
    result = sphinx_doctree("# One\n\n## Deep Two\n\n[](#deep-two)\n", "index.md")
    assert not result.warnings
    doctree = result.get_resolved_doctree("index")
    from docutils import nodes as docutils_nodes

    ref = next(doctree.findall(docutils_nodes.reference))
    assert ref.get("refid") == "deep-two", ref.attributes


def test_heading_anchors_html_ids_disabled_sphinx(sphinx_doctree: CreateDoctree):
    """The `myst_heading_anchors_html_ids=False` escape hatch works under sphinx."""
    sphinx_doctree.set_conf(
        {
            "extensions": ["myst_parser"],
            "myst_heading_anchors": 2,
            "myst_heading_anchors_html_ids": False,
        }
    )
    result = sphinx_doctree("# One\n\n## Ubuntu 20.04\n", "index.md")
    doctree = result.get_resolved_doctree("index")
    from docutils import nodes as docutils_nodes

    for section in doctree.findall(docutils_nodes.section):
        # only the docutils id: no secondary slug id was emitted
        assert len(section["ids"]) == 1, section["ids"]
        assert "slug" in section.attributes, section.attributes


def test_slug_id_stays_secondary_under_sortids(sphinx_doctree: CreateDoctree):
    """Sphinx's SortIds must not promote a slug to a section's primary id.

    Regression: for auto-generated (`idN`) ids — non-ASCII or digit-leading
    titles — SortIds rotated the docutils id to the back, silently changing
    toc/searchindex anchors to the slug.
    """
    sphinx_doctree.set_conf({"extensions": ["myst_parser"], "myst_heading_anchors": 2})
    result = sphinx_doctree("# Заголовок\n\n## Привет Мир\n", "index.md")
    doctree = result.get_resolved_doctree("index")
    from docutils import nodes as docutils_nodes

    for section in doctree.findall(docutils_nodes.section):
        assert section["ids"][0].startswith("id"), section["ids"]
        assert section["slug"] in section["ids"][1:], section["ids"]


@pytest.mark.parametrize(
    "test_name,text",
    [
        ("doc_root_anchor", '# Title\n\n[a](#index "TT")'),
        ("heading_anchor", '# Title\n\n## Section\n\n[a](#section "TT")'),
        ("explicit_target", '(target)=\n# Title\n\n[a](#target "TT")'),
        ("doc", '# Title\n\n[a](index.md "TT")'),
        ("doc_with_target_id", '(ref)=\n# Title\n\n[a](index.md#ref "TT")'),
        ("unresolved", '# Title\n\n[a](#nope "TT")'),
    ],
)
def test_link_title_is_kept(
    test_name: str, text: str, sphinx_doctree: CreateDoctree
) -> None:
    """A CommonMark link title must survive cross-reference resolution.

    Only two of these branches used to keep it; the rest built a fresh node
    and dropped the title on the way.
    """
    sphinx_doctree.set_conf({"extensions": ["myst_parser"]})
    doctree = sphinx_doctree(text, "index.md").get_resolved_doctree("index")
    titles = [
        node["reftitle"]
        for node in doctree.findall(nodes.reference)
        if "reftitle" in node
    ]
    assert titles == ["TT"], doctree.pformat()


PY_FUNCTION = "# Title\n\n```{py:function} myfunc()\n```\n\n"


def _reftitles(doctree: nodes.document) -> list[str]:
    return [
        node["reftitle"]
        for node in doctree.findall(nodes.reference)
        if "reftitle" in node
    ]


def test_link_title_beats_domain_title(sphinx_doctree: CreateDoctree) -> None:
    """The authored title wins over the title a domain puts on the reference.

    The py domain resolves `#myfunc` with ``reftitle="myfunc"``;
    an explicit ``"TT"`` written by the author must replace it,
    as it already does for intersphinx and for links to documents.
    """
    sphinx_doctree.set_conf({"extensions": ["myst_parser"]})
    result = sphinx_doctree(PY_FUNCTION + '[a](#myfunc "TT")\n', "index.md")
    assert not result.warnings
    assert _reftitles(result.get_resolved_doctree("index")) == ["TT"]


def test_link_without_title_keeps_domain_title(sphinx_doctree: CreateDoctree) -> None:
    """Without an authored title, the domain's own title is left alone."""
    sphinx_doctree.set_conf({"extensions": ["myst_parser"]})
    result = sphinx_doctree(PY_FUNCTION + "[a](#myfunc)\n", "index.md")
    assert not result.warnings
    assert _reftitles(result.get_resolved_doctree("index")) == ["myfunc"]


@pytest.mark.parametrize(
    "text",
    [
        pytest.param('# Title\n\n[a](index.md "TT")', id="doc"),
        pytest.param(PY_FUNCTION + '[a](#myfunc "TT")', id="any"),
    ],
)
def test_link_title_not_set_without_uri(
    text: str, sphinx_doctree: CreateDoctree, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When the builder has no URI for the target (`NoUri`),
    the link is replaced by its bare inline content, which takes no title.
    """
    from sphinx.errors import NoUri

    from myst_parser.sphinx_ext import myst_refs

    def no_uri(*args, **kwargs):
        raise NoUri

    monkeypatch.setattr(myst_refs, "make_refnode", no_uri)
    monkeypatch.setattr(myst_refs.MystReferenceResolver, "resolve_myst_ref_any", no_uri)
    sphinx_doctree.set_conf({"extensions": ["myst_parser"]})
    doctree = sphinx_doctree(text, "index.md").get_resolved_doctree("index")
    assert not list(doctree.findall(nodes.reference)), doctree.pformat()
    assert not [
        node for node in doctree.findall(nodes.Element) if "reftitle" in node
    ], doctree.pformat()


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("# Title\n\n## Section\n\n[a](#section 'TT')", id="slug"),
        pytest.param("# Title\n\n## Section\n\n### Deep\n\n[a](#deep 'TT')", id="deep"),
    ],
)
def test_link_title_kept_with_heading_anchors(
    text: str, sphinx_doctree: CreateDoctree
) -> None:
    """With `myst_heading_anchors`, a slug link and a link to a heading beyond
    the anchor depth (resolved by the local fallback) both keep the title."""
    sphinx_doctree.set_conf({"extensions": ["myst_parser"], "myst_heading_anchors": 2})
    result = sphinx_doctree(text, "index.md")
    assert not result.warnings
    assert _reftitles(result.get_resolved_doctree("index")) == ["TT"]


def test_link_title_kept_across_documents(sphinx_doctree: CreateDoctree) -> None:
    """Links to another document, to a target in it, and to its label by name
    all keep the title."""
    sphinx_doctree.set_conf(
        {"extensions": ["myst_parser"], "suppress_warnings": ["toc.not_included"]}
    )
    sphinx_doctree.srcdir.joinpath("other.md").write_text(
        "# Other\n\n(lbl)=\n## Part\n", encoding="utf8"
    )
    result = sphinx_doctree(
        '# Title\n\n[a](other.md "T1") [b](other.md#lbl "T2") [c](#lbl "T3")\n',
        "index.md",
    )
    assert not result.warnings
    assert _reftitles(result.get_resolved_doctree("index")) == ["T1", "T2", "T3"]


def test_link_title_from_attrs(sphinx_doctree: CreateDoctree) -> None:
    """A `{title="..."}` attribute is an authored title too."""
    sphinx_doctree.set_conf(
        {
            "extensions": ["myst_parser"],
            "myst_enable_extensions": ["attrs_inline"],
            "suppress_warnings": ["toc.not_included"],
        }
    )
    sphinx_doctree.srcdir.joinpath("other.md").write_text("# Other\n", encoding="utf8")
    result = sphinx_doctree(
        PY_FUNCTION + '[a](other.md){title="T1"} [b](#myfunc){title="T2"}\n',
        "index.md",
    )
    assert not result.warnings
    assert _reftitles(result.get_resolved_doctree("index")) == ["T1", "T2"]


def test_link_without_title_gets_none(sphinx_doctree: CreateDoctree) -> None:
    """Links without a title get no `reftitle` on any resolution path."""
    sphinx_doctree.set_conf(
        {"extensions": ["myst_parser"], "suppress_warnings": ["toc.not_included"]}
    )
    sphinx_doctree.srcdir.joinpath("other.md").write_text(
        "# Other\n\n(lbl)=\n## Part\n", encoding="utf8"
    )
    doctree = sphinx_doctree(
        "(target)=\n# Title\n\n"
        "[a](#target) [b](#title) [c](other.md) [d](other.md#lbl) [e](#lbl) [f](#nope)\n",
        "index.md",
    ).get_resolved_doctree("index")
    assert len(list(doctree.findall(nodes.reference))) == 6, doctree.pformat()
    assert _reftitles(doctree) == [], doctree.pformat()


def test_link_title_in_html(make_app, tmp_path) -> None:
    """The title reaches the `<a>` tag of the HTML output."""
    srcdir = tmp_path / "src"
    srcdir.mkdir()
    srcdir.joinpath("conf.py").write_text(
        'extensions = ["myst_parser"]\nsuppress_warnings = ["toc.not_included"]\n',
        encoding="utf8",
    )
    srcdir.joinpath("other.md").write_text("# Other\n", encoding="utf8")
    srcdir.joinpath("index.md").write_text(
        PY_FUNCTION + '[a](other.md "T1") [b](#myfunc "T2")\n', encoding="utf8"
    )
    app = make_app("html", srcdir=srcdir)
    app.build()
    html = (app.outdir / "index.html").read_text(encoding="utf8")
    assert 'href="other.html" title="T1"' in html, html
    assert 'title="T2"' in html, html
    assert 'title="myfunc"' not in html, html
