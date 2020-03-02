"""Uses sphinx's pytest fixture to run builds.

see conftest.py for fixture usage
"""
import os

import pytest


SOURCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "sourcedirs"))


@pytest.mark.sphinx(
    buildername="html", srcdir=os.path.join(SOURCE_DIR, "basic"), freshenv=True
)
def test_basic(app, status, warning, get_sphinx_app_output, remove_sphinx_builds):
    """basic test."""
    app.build()

    assert "build succeeded" in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert warnings == ""

    get_sphinx_app_output(app, filename="content.html", regress_html=True)


@pytest.mark.sphinx(
    buildername="html", srcdir=os.path.join(SOURCE_DIR, "includes"), freshenv=True
)
def test_includes(
    app,
    status,
    warning,
    get_sphinx_app_doctree,
    get_sphinx_app_output,
    remove_sphinx_builds,
):
    """Test of include directive."""
    app.build()

    assert "build succeeded" in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert warnings == ""

    get_sphinx_app_doctree(app, filename="index.doctree", regress=True)
    get_sphinx_app_output(app, filename="index.html", regress_html=True)


@pytest.mark.sphinx(
    buildername="html", srcdir=os.path.join(SOURCE_DIR, "bibtex_norefs"), freshenv=True
)
def test_bibtex_norefs(
    app,
    status,
    warning,
    get_sphinx_app_doctree,
    get_sphinx_app_output,
    remove_sphinx_builds,
):
    """Test of spinxcontrib-bibtex extension."""
    app.build()

    assert "build succeeded" in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert "citation not found: abc" in warnings

    get_sphinx_app_doctree(app, filename="index.doctree", regress=True)
    get_sphinx_app_output(app, filename="index.html", regress_html=True)
