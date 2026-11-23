"""Tests for the scoped Sphinx include footnote transform."""

from docutils import nodes
from docutils.utils import new_document

from myst_parser.mdit_to_docutils.transforms import RegisterIncludedFootnotes


def test_only_myst_footnotes_are_registered():
    """Do not take ownership of unregistered nodes from another parser."""
    document = new_document("test")
    other = nodes.footnote(auto=1, names=["other"])
    myst = nodes.footnote(auto=1, names=["myst"])
    myst._myst_footnote = True
    other_ref = nodes.footnote_reference(auto=1, refname="other")
    myst_ref = nodes.footnote_reference(auto=1, refname="myst")
    myst_ref._myst_footnote = True
    document.extend([nodes.paragraph("", "", other_ref, myst_ref), other, myst])

    RegisterIncludedFootnotes(document).apply()

    assert document.autofootnotes == [myst]
    assert document.nameids.get("myst") == myst["ids"][0]
    assert document.autofootnote_refs == [myst_ref]
    assert document.footnote_refs == {"myst": [myst_ref]}
    assert "other" not in document.nameids
    assert other["ids"] == []
