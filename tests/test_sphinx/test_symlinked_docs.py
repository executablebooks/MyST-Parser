"""Links to a document that is a symlink to a file outside the source directory."""

from __future__ import annotations

import os
from io import StringIO
from pathlib import Path

import pytest
from sphinx.application import Sphinx


def _build(srcdir: Path, outdir: Path) -> tuple[str, str]:
    """Build the project with the html builder, return (warnings, index.html)."""
    status, warning = StringIO(), StringIO()
    app = Sphinx(
        str(srcdir),
        str(srcdir),
        str(outdir),
        str(outdir / ".doctrees"),
        "html",
        status=status,
        warning=warning,
        freshenv=True,
    )
    app.build()
    return warning.getvalue(), (outdir / "index.html").read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "link",
    [
        pytest.param("linked.md#target-section", id="relative-path"),
        pytest.param("project:linked.md#target-section", id="project-scheme"),
    ],
)
def test_link_to_symlinked_doc_outside_srcdir(tmp_path: Path, link: str):
    """A link to a document that is a symlink to a file outside the source
    directory resolves to the document, rather than to the symlink target.
    """
    docs = tmp_path / "project" / "docs"
    docs.mkdir(parents=True)
    (tmp_path / "project" / "README.md").write_text(
        "# Readme\n\n## Target section\n\ntext\n", encoding="utf-8"
    )
    try:
        os.symlink(os.path.join("..", "README.md"), docs / "linked.md")
    except (OSError, NotImplementedError):  # pragma: no cover
        pytest.skip("symlinks are not available")
    (docs / "conf.py").write_text(
        'extensions = ["myst_parser"]\nmyst_heading_anchors = 3\n', encoding="utf-8"
    )
    (docs / "index.md").write_text(
        f"# Index\n\n[Section title]({link})\n\n```{{toctree}}\nlinked\n```\n",
        encoding="utf-8",
    )

    warnings, index_html = _build(docs, tmp_path / "_build")

    assert "Unknown source document" not in warnings
    assert "Could not find document" not in warnings
    assert 'href="linked.html#target-section"' in index_html
