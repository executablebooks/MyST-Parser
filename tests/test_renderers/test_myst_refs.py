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
        assert section["slug"] not in section["ids"], section["ids"]


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
