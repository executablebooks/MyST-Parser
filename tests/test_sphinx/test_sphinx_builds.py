"""Uses sphinx's pytest fixture to run builds.

see conftest.py for fixture usage
"""
import os

import pytest


SOURCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "sourcedirs"))


@pytest.mark.sphinx(
    buildername="html", srcdir=os.path.join(SOURCE_DIR, "basic"), freshenv=True
)
def test_basic(
    app,
    status,
    warning,
    get_sphinx_app_doctree,
    get_sphinx_app_output,
    remove_sphinx_builds,
):
    """basic test."""
    app.build()

    assert "build succeeded" in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert warnings == ""

    get_sphinx_app_doctree(app, docname="content", regress=True)
    get_sphinx_app_doctree(app, docname="content", resolve=True, regress=True)
    get_sphinx_app_output(app, filename="content.html", regress_html=True)


@pytest.mark.sphinx(
    buildername="html",
    srcdir=os.path.join(SOURCE_DIR, "references"),
    freshenv=True,
)
def test_references(
    app,
    status,
    warning,
    get_sphinx_app_doctree,
    get_sphinx_app_output,
    remove_sphinx_builds,
):
    """Test reference resolution."""
    app.build()

    assert "build succeeded" in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert warnings == ""

    try:
        get_sphinx_app_doctree(app, docname="index", regress=True)
    finally:
        get_sphinx_app_doctree(app, docname="index", resolve=True, regress=True)
    get_sphinx_app_output(app, filename="index.html", regress_html=True)


@pytest.mark.sphinx(
    buildername="singlehtml",
    srcdir=os.path.join(SOURCE_DIR, "references_singlehtml"),
    freshenv=True,
    confoverrides={"nitpicky": True},
)
def test_references_singlehtml(
    app,
    status,
    warning,
    get_sphinx_app_doctree,
    get_sphinx_app_output,
    remove_sphinx_builds,
):
    """Test reference resolution for singlehtml builds."""
    app.build()

    assert "build succeeded" in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert warnings == ""

    # try:
    #     get_sphinx_app_doctree(app, docname="index", regress=True)
    # finally:
    #     get_sphinx_app_doctree(app, docname="index", resolve=True, regress=True)

    try:
        get_sphinx_app_doctree(
            app,
            docname="other/other",
            regress=True,
            replace={"other\\other.md": "other/other.md"},
        )
    finally:
        get_sphinx_app_doctree(
            app,
            docname="other/other",
            resolve=True,
            regress=True,
            replace={"other\\other.md": "other/other.md"},
        )

    get_sphinx_app_output(
        app, filename="index.html", buildername="singlehtml", regress_html=True
    )


@pytest.mark.sphinx(
    buildername="html",
    srcdir=os.path.join(SOURCE_DIR, "extended_syntaxes"),
    freshenv=True,
)
def test_extended_syntaxes(
    app,
    status,
    warning,
    get_sphinx_app_doctree,
    get_sphinx_app_output,
    remove_sphinx_builds,
    monkeypatch,
):
    """test setting addition configuration values."""
    from myst_parser.sphinx_renderer import SphinxRenderer

    monkeypatch.setattr(SphinxRenderer, "_random_label", lambda self: "mock-uuid")
    app.build()
    assert "build succeeded" in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    # TODO turn back on when deprecations removed after v0.13.0
    # assert warnings == ""
    assert "`myst_figure_enable` is deprecated" in warnings
    assert "comma-separated classes are deprecated" in warnings
    assert ":::{figure} is deprecated" in warnings

    try:
        get_sphinx_app_doctree(app, docname="index", regress=True)
    finally:
        get_sphinx_app_output(app, filename="index.html", regress_html=True)


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

    try:
        get_sphinx_app_doctree(
            app,
            docname="index",
            regress=True,
            # fix for Windows CI
            replace={
                r"subfolder\example2.jpg": "subfolder/example2.jpg",
                r"subfolder\\example2.jpg": "subfolder/example2.jpg",
                r"subfolder\\\\example2.jpg": "subfolder/example2.jpg",
            },
        )
    finally:
        get_sphinx_app_output(
            app,
            filename="index.html",
            regress_html=True,
            replace={
                r"'subfolder\\example2'": "'subfolder/example2'",
                r'uri="subfolder\\example2"': 'uri="subfolder/example2"',
                "_images/example21.jpg": "_images/example2.jpg",
            },
        )


@pytest.mark.sphinx(
    buildername="html", srcdir=os.path.join(SOURCE_DIR, "footnotes"), freshenv=True
)
def test_footnotes(
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

    try:
        get_sphinx_app_doctree(app, docname="footnote_md", regress=True)
    finally:
        get_sphinx_app_output(app, filename="footnote_md.html", regress_html=True)


@pytest.mark.sphinx(
    buildername="html",
    srcdir=os.path.join(SOURCE_DIR, "commonmark_only"),
    freshenv=True,
)
def test_commonmark_only(
    app,
    status,
    warning,
    get_sphinx_app_doctree,
    get_sphinx_app_output,
    remove_sphinx_builds,
):
    """test setting addition configuration values."""
    app.build()
    assert "build succeeded" in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert "lexer name '{note}'" in warnings

    try:
        get_sphinx_app_doctree(app, docname="index", regress=True)
    finally:
        get_sphinx_app_output(app, filename="index.html", regress_html=True)
