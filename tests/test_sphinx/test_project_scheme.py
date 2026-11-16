"""`project:` references stay inside the current project."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

SOURCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "sourcedirs"))
INVENTORY_URL = "https://example.com/index.html#paragraph-target"


@pytest.mark.sphinx(
    buildername="html",
    srcdir=os.path.join(SOURCE_DIR, "project_scheme"),
    freshenv=True,
    confoverrides={"show_warning_types": True},
)
def test_project_scheme_does_not_use_intersphinx(app, status, warning):
    """A missing `project:` target warns, and a plain `#` link still uses the inventory."""
    app.build()

    assert "build succeeded" in status.getvalue()
    warnings = warning.getvalue()
    assert warnings.count("target not found: 'paragraph-target'") == 2
    assert "local-heading" not in warnings
    assert "[myst.xref_missing]" in warnings

    html = Path(app.outdir, "index.html").read_text(encoding="utf-8")
    before, after = html.split("Hash still uses the inventory", maxsplit=1)
    assert INVENTORY_URL not in before
    assert after.count(INVENTORY_URL) == 1
    assert ">explicit</" in before or ">explicit<" in before
