"""Integration tests for Markdown footnotes included in reStructuredText."""

import os

import pytest
from bs4 import BeautifulSoup

SOURCE_DIR = os.path.join(os.path.dirname(__file__), "sourcedirs")


@pytest.mark.sphinx(
    buildername="html",
    srcdir=os.path.join(SOURCE_DIR, "rst_include_footnotes"),
    freshenv=True,
)
def test_rst_include_footnotes(app, warning):
    """Included references share the host's numbering and unique identifiers."""
    app.build()
    assert warning.getvalue().strip() == ""

    html = (app.outdir / "index.html").read_text(encoding="utf8")
    soup = BeautifulSoup(html, "html.parser")
    refs = soup.select("a.footnote-reference")
    notes = soup.select("aside.footnote")
    assert [ref.get_text(strip=True) for ref in refs] == ["[1]", "[2]", "[3]", "[4]"]
    assert [note.select_one("span.label").get_text(strip=True) for note in notes] == [
        "[1]",
        "[2]",
        "[3]",
        "[4]",
    ]
    ids = [node["id"] for node in soup.select("[id]")]
    assert len(ids) == len(set(ids))
    assert [ref["href"] for ref in refs] == [f"#{note['id']}" for note in notes]


@pytest.mark.sphinx(
    buildername="html",
    srcdir=os.path.join(SOURCE_DIR, "rst_include_footnotes_cross"),
    freshenv=True,
)
def test_rst_include_cross_references(app, warning):
    """Footnotes can be referenced from either side of the include."""
    app.build()
    assert warning.getvalue().strip() == ""

    html = (app.outdir / "index.html").read_text(encoding="utf8")
    soup = BeautifulSoup(html, "html.parser")
    refs = soup.select("a.footnote-reference")
    assert [ref.get_text(strip=True) for ref in refs] == [
        "[1]",
        "[2]",
        "[2]",
        "[1]",
        "[9]",
        "[3]",
    ]
    targets = [soup.select_one(ref["href"]) for ref in refs]
    assert all(target is not None for target in targets)
    assert targets[0] is targets[3]
    assert targets[1] is targets[2]
    assert "Numeric footnote" in targets[4].get_text()
    ids = [node["id"] for node in soup.select("[id]")]
    assert len(ids) == len(set(ids))
