import sys

import pytest
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


_LINK_TEXT_OTHER_MD = """\
# Other

(my-label)=
## Labelled heading

(colon:label)=
## Colon heading

## Snake_case heading

### Third level

(deep-label)=
#### Deep heading

(para-label)=
A paragraph.

```{figure} img.png
:name: fig-label

Figure caption
```
"""

_LINK_TEXT_RST_DOC = """\
RST document
============

.. _rst-label:

RST section
-----------

Text.
"""


def _write_link_text_docs(sphinx_doctree: CreateDoctree, heading_anchors: int | None):
    conf: dict = {"extensions": ["myst_parser"], "show_warning_types": True}
    if heading_anchors is not None:
        conf["myst_heading_anchors"] = heading_anchors
    sphinx_doctree.set_conf(conf)
    sphinx_doctree.srcdir.joinpath("other.md").write_text(
        _LINK_TEXT_OTHER_MD, encoding="utf8"
    )
    sphinx_doctree.srcdir.joinpath("rstdoc.rst").write_text(
        _LINK_TEXT_RST_DOC, encoding="utf8"
    )
    sphinx_doctree.srcdir.joinpath("img.png").write_bytes(b"")


@pytest.mark.parametrize(
    "heading_anchors", [2, None], ids=["heading_anchors", "no_heading_anchors"]
)
@pytest.mark.parametrize(
    "link,expected",
    [
        # an explicit label on a heading, which becomes the section's id
        ("[](other.md#my-label)", "Labelled heading"),
        # a label referenced by name, rather than by its id
        ("[](other.md#colon:label)", "Colon heading"),
        ("[](other.md#colon-label)", "Colon heading"),
        # a label on a heading beyond the `myst_heading_anchors` depth
        ("[](other.md#deep-label)", "Deep heading"),
        # a label on a figure uses the figure's caption
        ("[](other.md#fig-label)", "Figure caption"),
        # a label in an rST document uses its section title
        ("[](rstdoc.rst#rst-label)", "RST section"),
        # explicit link text is kept
        ("[custom](other.md#my-label)", "custom"),
        # an anonymous label has no title, so the target is shown
        ("[](other.md#para-label)", "para-label"),
    ],
)
def test_doc_with_target_link_text(
    link: str,
    expected: str,
    heading_anchors: int | None,
    sphinx_doctree: CreateDoctree,
):
    """`[](doc.md#target)` to an explicit target uses the target's title.

    Regression: links that resolved through a label or a section id, rather
    than a heading slug, rendered with no link text at all.
    The title must come from the label itself, not from heading slugs,
    so the same holds with `myst_heading_anchors` unset.
    """
    from docutils import nodes as docutils_nodes

    _write_link_text_docs(sphinx_doctree, heading_anchors)
    result = sphinx_doctree(f"# Index\n\n{link}\n", "index.md")
    doctree = result.get_resolved_doctree("index")
    # checked after resolution, which is where reference warnings are emitted
    assert not result.warnings, result.warnings
    ref = next(doctree.findall(docutils_nodes.reference))
    assert ref.astext() == expected, ref.pformat()


def test_doc_with_section_id_link_text(sphinx_doctree: CreateDoctree):
    """`[](doc.md#id)` to a section's docutils id, not its slug, uses its title.

    The heading's slug (``snake_case-heading``) and its docutils id
    (``snake-case-heading``) differ, so this resolves through the section id.
    """
    from docutils import nodes as docutils_nodes

    _write_link_text_docs(sphinx_doctree, 2)
    result = sphinx_doctree("# Index\n\n[](other.md#snake-case-heading)\n", "index.md")
    doctree = result.get_resolved_doctree("index")
    assert not result.warnings, result.warnings
    ref = next(doctree.findall(docutils_nodes.reference))
    assert ref.astext() == "Snake_case heading", ref.pformat()
    assert ref["refuri"].endswith("#snake-case-heading"), ref.attributes


def test_doc_with_missing_target_link_text(sphinx_doctree: CreateDoctree):
    """`[](doc.md#missing)` warns once, and shows the id rather than nothing.

    The link still points at the requested id, as it did before.
    """
    from docutils import nodes as docutils_nodes

    _write_link_text_docs(sphinx_doctree, 2)
    result = sphinx_doctree("# Index\n\n[](other.md#missing-id)\n", "index.md")
    doctree = result.get_resolved_doctree("index")
    warnings = [line for line in result.warnings.splitlines() if line.strip()]
    assert len(warnings) == 1, result.warnings
    assert "local id not found in doc 'other': 'missing-id'" in warnings[0]
    assert "[myst.xref_missing]" in warnings[0]
    ref = next(doctree.findall(docutils_nodes.reference))
    assert ref.astext() == "missing-id", ref.pformat()
    # (the test builder gives documents an empty uri, so only the fragment shows)
    assert ref["refuri"].endswith("#missing-id"), ref.attributes
