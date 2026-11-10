"""``§1.1`` section references resolve to the same heading in docutils and sphinx.

docutils promotes a lone top-level heading to the document title
(and a lone child heading of that to the subtitle), but sphinx never does,
so the two doctrees differ in shape.
The references are resolved before that promotion, against the headings as written,
so each case is checked against both parsers, with the same expected result;
a resolution that ran after the promotion would fail the docutils side.
"""

from __future__ import annotations

import io

import pytest
from docutils import nodes
from docutils.core import publish_doctree
from sphinx_pytest.plugin import CreateDoctree

from myst_parser.parsers.docutils_ import Parser

CASES = [
    pytest.param(
        "# T\n\n## A\n\n### A1\n\n## B\n\nSee §1 §1.1 §2.\n",
        [("§1", "a"), ("§1.1", "a1"), ("§2", "b")],
        [],
        id="title-and-two-sections",
    ),
    pytest.param(
        # docutils promotes T to the title, leaving A as the only section;
        # A is still §1, not the root whose children are numbered
        "# T\n\nSee §1 and §1.1.\n\n## A\n\n### A1\n",
        [("§1", "a"), ("§1.1", "a1")],
        [],
        id="title-and-one-section",
    ),
    pytest.param(
        # docutils also promotes A to the subtitle, as T holds nothing else
        "# T\n\n## A\n\nSee §1 and §1.1.\n\n### B\n",
        [("§1", "a"), ("§1.1", "b")],
        [],
        id="subtitle",
    ),
    pytest.param(
        "# T\n\n## A\n\nSee §1, not §2.\n",
        [("§1", "a")],
        ["§2"],
        id="subtitle-only",
    ),
    pytest.param(
        # a reference in the subtitle stays inert, as it does in the heading
        "# T\n\n## A §1\n\nSee §1 and §1.1.\n\n### B\n",
        [("§1", "a-1"), ("§1.1", "b")],
        ["§1"],
        id="reference-in-subtitle",
    ),
    pytest.param(
        "## A\n\nSee §1 and §1.1.\n\n### A1\n",
        [("§1", "a1")],
        ["§1.1"],
        id="single-root-below-h1",
    ),
    pytest.param(
        "See §1 and §2.\n\n# A\n\n# B\n",
        [("§1", "a"), ("§2", "b")],
        [],
        id="several-top-level",
    ),
    pytest.param(
        # a reference in link text stays inert
        "# T\n\n## A\n\n[see §1](#a)\n",
        [],
        ["§1"],
        id="reference-in-anchor-link",
    ),
    pytest.param(
        # the link goes to the explicit target's id, the section's first id
        "# T\n\n(lbl)=\n## A\n\n## B\n\nSee §1.\n",
        [("§1", "lbl")],
        [],
        id="explicit-target",
    ),
    pytest.param(
        # only section headings are inert, other titles are not
        "# T\n\n## A\n\n```{admonition} See §1\nx\n```\n",
        [("§1", "a")],
        [],
        id="reference-in-admonition-title",
    ),
    pytest.param(
        # text before the heading means docutils promotes nothing
        "See §1.\n\n# T\n\n## A\n",
        [("§1", "a")],
        [],
        id="no-promotion",
    ),
]


def _summarise(doctree: nodes.document) -> tuple[list, list]:
    """Return the resolved ``(text, refid)`` pairs and the texts left unresolved."""
    resolved = [
        (ref.astext(), ref["refid"])
        for ref in doctree.findall(nodes.reference)
        if "section-ref" in ref["classes"]
    ]
    unresolved = [
        node.astext()
        for node in doctree.findall(nodes.inline)
        if "section_numbers" in node
    ]
    return resolved, unresolved


@pytest.mark.parametrize("source,resolved,unresolved", CASES)
def test_docutils(source: str, resolved: list, unresolved: list):
    doctree = publish_doctree(
        source,
        parser=Parser(),
        settings_overrides={
            "myst_enable_extensions": ["section_ref"],
            "warning_stream": io.StringIO(),
        },
    )
    assert _summarise(doctree) == (resolved, unresolved)


@pytest.mark.parametrize("source,resolved,unresolved", CASES)
def test_sphinx(
    source: str,
    resolved: list,
    unresolved: list,
    sphinx_doctree: CreateDoctree,
):
    sphinx_doctree.set_conf(
        {"extensions": ["myst_parser"], "myst_enable_extensions": ["section_ref"]}
    )
    result = sphinx_doctree(source, "index.md")
    assert _summarise(result.doctrees["index"]) == (resolved, unresolved)


def test_sphinx_reference_in_document_link(sphinx_doctree: CreateDoctree):
    """A reference in the text of a link to another document stays inert.

    sphinx parses such a link to a ``pending_xref`` rather than a ``reference``
    (docutils cannot resolve it at all, so this case is sphinx-only).
    """
    sphinx_doctree.set_conf(
        {"extensions": ["myst_parser"], "myst_enable_extensions": ["section_ref"]}
    )
    result = sphinx_doctree("# T\n\n## A\n\n[see §1](other.md)\n", "index.md")
    doctree = result.doctrees["index"]
    assert any(node.tagname == "pending_xref" for node in doctree.findall())
    assert _summarise(doctree) == ([], ["§1"])


def test_docutils_without_doctitle_promotion():
    """With ``doctitle_xform`` off, docutils keeps the headings as sphinx does."""
    doctree = publish_doctree(
        "# T\n\nSee §1 and §1.1.\n\n## A\n\n### A1\n",
        parser=Parser(),
        settings_overrides={
            "myst_enable_extensions": ["section_ref"],
            "doctitle_xform": False,
        },
    )
    assert _summarise(doctree) == ([("§1", "a"), ("§1.1", "a1")], [])


def test_docutils_section_subtitles():
    """With ``sectsubtitle_xform`` on, references still follow the headings as written.

    docutils' ``SectSubTitle`` transform promotes C, the lone subsection of B,
    to B's subtitle, but C is still ``§1.1.1``, as it is in sphinx.
    """
    doctree = publish_doctree(
        "# T\n\n## A\n\nSee §1.1 and §1.1.1.\n\n### B\n\n#### C\n\nx\n",
        parser=Parser(),
        settings_overrides={
            "myst_enable_extensions": ["section_ref"],
            "sectsubtitle_xform": True,
        },
    )
    assert any(
        isinstance(node.parent, nodes.section)
        for node in doctree.findall(nodes.subtitle)
    ), "the section subtitle promotion did not happen"
    assert _summarise(doctree) == ([("§1.1", "b"), ("§1.1.1", "c")], [])


def test_docutils_warning_location_in_include(tmp_path):
    """An unresolved reference in an included file is reported at that file."""
    (tmp_path / "index.md").write_text(
        "# T\n\n## A\n\n```{include} sub.md\n```\n", encoding="utf8"
    )
    (tmp_path / "sub.md").write_text("Para\n\nSee §7.\n", encoding="utf8")
    warnings = io.StringIO()
    publish_doctree(
        (tmp_path / "index.md").read_text(encoding="utf8"),
        source_path=str(tmp_path / "index.md"),
        parser=Parser(),
        settings_overrides={
            "myst_enable_extensions": ["section_ref"],
            "warning_stream": warnings,
        },
    )
    location = f"{tmp_path / 'sub.md'}:3: (WARNING/2)"
    assert f"{location} Section reference target not found" in warnings.getvalue()


def test_subtitle_tooltip():
    """A reference to the promoted subtitle carries its text as the tooltip."""
    doctree = publish_doctree(
        "# T\n\n## The *A*\n\nSee §1.\n",
        parser=Parser(),
        settings_overrides={"myst_enable_extensions": ["section_ref"]},
    )
    (ref,) = (
        ref
        for ref in doctree.findall(nodes.reference)
        if "section-ref" in ref["classes"]
    )
    assert ref["reftitle"] == "The A"
