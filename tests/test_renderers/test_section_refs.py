"""``§1.1`` section references resolve to the same heading in docutils and sphinx.

docutils promotes a lone top-level heading to the document title
(and a lone child heading of that to the subtitle), but sphinx never does,
so the two doctrees differ in shape.
The numbering is that of the headings as written, so each case is checked
against both parsers, with the same expected result.
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
