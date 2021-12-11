"""Uses sphinx's pytest fixture to run builds.

see conftest.py for fixture usage

NOTE: sphinx 3 & 4 regress against different output files,
the major difference being sphinx 4 uses docutils 0.17,
which uses semantic HTML tags
(e.g. converting `<div class="section">` to `<section>`)
"""
import os
import re

import pytest
import sphinx
from docutils import VersionInfo, __version_info__

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

    get_sphinx_app_doctree(
        app,
        docname="content",
        regress=True,
        regress_ext=f".sphinx{sphinx.version_info[0]}.xml",
    )
    get_sphinx_app_doctree(
        app,
        docname="content",
        resolve=True,
        regress=True,
        regress_ext=f".sphinx{sphinx.version_info[0]}.xml",
    )
    get_sphinx_app_output(
        app,
        filename="content.html",
        regress_html=True,
        regress_ext=f".sphinx{sphinx.version_info[0]}.html",
    )

    assert app.env.metadata["content"] == {
        "author": "Chris Sewell",
        "authors": ["Chris Sewell", "Chris Hodgraf"],
        "organization": "EPFL",
        "address": "1 Cedar Park Close\nThundersley\nEssex\n",
        "contact": "https://example.com",
        "version": "1.0",
        "revision": "1.1",
        "status": "good",
        "date": "2/12/1985",
        "copyright": "MIT",
        "other": "Something else",
        "wordcount": {"minutes": 0, "words": 53},
    }


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
    get_sphinx_app_output(
        app,
        filename="index.html",
        regress_html=True,
        regress_ext=f".sphinx{sphinx.version_info[0]}.html",
    )


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
        app,
        filename="index.html",
        buildername="singlehtml",
        regress_html=True,
        regress_ext=f".sphinx{sphinx.version_info[0]}.html",
    )


@pytest.mark.sphinx(
    buildername="html",
    srcdir=os.path.join(SOURCE_DIR, "heading_slug_func"),
    freshenv=True,
)
def test_heading_slug_func(
    app,
    status,
    warning,
    get_sphinx_app_doctree,
    get_sphinx_app_output,
    remove_sphinx_builds,
):
    """Test heading_slug_func configuration."""
    app.build()

    assert "build succeeded" in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert warnings == ""

    try:
        get_sphinx_app_doctree(app, docname="index", regress=True)
    finally:
        get_sphinx_app_doctree(app, docname="index", resolve=True, regress=True)
    get_sphinx_app_output(
        app,
        filename="index.html",
        regress_html=True,
        regress_ext=f".sphinx{sphinx.version_info[0]}.html",
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
    assert warnings == ""

    try:
        get_sphinx_app_doctree(
            app,
            docname="index",
            regress=True,
            regress_ext=f".sphinx{sphinx.version_info[0]}.xml",
        )
    finally:
        get_sphinx_app_output(
            app,
            filename="index.html",
            regress_html=True,
            regress_ext=f".sphinx{sphinx.version_info[0]}.html",
        )


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
            regress_ext=f".sphinx{sphinx.version_info[0]}.xml",
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
            regress_ext=f".sphinx{sphinx.version_info[0]}.html",
            replace={
                r"'subfolder\\example2'": "'subfolder/example2'",
                r'uri="subfolder\\example2"': 'uri="subfolder/example2"',
                "_images/example21.jpg": "_images/example2.jpg",
            },
        )


@pytest.mark.skipif(
    __version_info__ < VersionInfo(0, 17, 0, "final", 0, True),
    reason="parser option added in docutils 0.17",
)
@pytest.mark.sphinx(
    buildername="html",
    srcdir=os.path.join(SOURCE_DIR, "include_from_rst"),
    freshenv=True,
)
def test_include_from_rst(
    app,
    status,
    warning,
    get_sphinx_app_doctree,
    get_sphinx_app_output,
    remove_sphinx_builds,
):
    """Test of include directive inside RST file."""
    app.build()

    assert "build succeeded" in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert warnings == ""

    get_sphinx_app_doctree(
        app,
        docname="index",
        regress=True,
        regress_ext=".xml",
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
        get_sphinx_app_output(
            app,
            filename="footnote_md.html",
            regress_html=True,
            regress_ext=f".sphinx{sphinx.version_info[0]}.html",
        )


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
        get_sphinx_app_output(
            app,
            filename="index.html",
            regress_html=True,
            regress_ext=f".sphinx{sphinx.version_info[0]}.html",
        )


@pytest.mark.sphinx(
    buildername="html",
    srcdir=os.path.join(SOURCE_DIR, "substitutions"),
    freshenv=True,
)
def test_substitutions(
    app,
    status,
    warning,
    get_sphinx_app_doctree,
    get_sphinx_app_output,
    remove_sphinx_builds,
    file_regression,
):
    """test setting addition configuration values."""
    app.build()
    assert "build succeeded" in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert warnings == ""

    try:
        get_sphinx_app_doctree(app, docname="index", regress=True)
        file_regression.check(
            get_sphinx_app_doctree(app, docname="other").pformat(),
            extension=".other.xml",
        )
    finally:
        get_sphinx_app_output(app, filename="index.html", regress_html=True)


@pytest.mark.sphinx(
    buildername="gettext", srcdir=os.path.join(SOURCE_DIR, "gettext"), freshenv=True
)
def test_gettext(
    app,
    status,
    warning,
    get_sphinx_app_output,
    remove_sphinx_builds,
    file_regression,
):
    """Test gettext message extraction."""
    app.build()
    assert "build succeeded" in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert warnings == ""

    output = get_sphinx_app_output(app, filename="index.pot", buildername="gettext")
    output = re.sub(r"POT-Creation-Date: [0-9: +-]+", "POT-Creation-Date: ", output)
    output = re.sub(r"Copyright \(C\) [0-9]{4}", "Copyright (C) XXXX", output)

    file_regression.check(output, extension=f".sphinx{sphinx.version_info[0]}.pot")


@pytest.mark.sphinx(
    buildername="html",
    srcdir=os.path.join(SOURCE_DIR, "gettext"),
    freshenv=True,
    confoverrides={"language": "fr", "gettext_compact": False, "locale_dirs": ["."]},
)
def test_gettext_html(
    app,
    status,
    warning,
    get_sphinx_app_doctree,
    get_sphinx_app_output,
    remove_sphinx_builds,
):
    """Test gettext message extraction."""
    app.build()
    assert "build succeeded" in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert warnings == ""

    try:
        get_sphinx_app_doctree(
            app,
            docname="index",
            regress=True,
            regress_ext=f".sphinx{sphinx.version_info[0]}.xml",
        )
    finally:
        get_sphinx_app_doctree(
            app,
            docname="index",
            resolve=True,
            regress=True,
            regress_ext=f".sphinx{sphinx.version_info[0]}.xml",
        )
    get_sphinx_app_output(
        app,
        filename="index.html",
        regress_html=True,
        regress_ext=f".sphinx{sphinx.version_info[0]}.html",
    )


@pytest.mark.sphinx(
    buildername="gettext",
    srcdir=os.path.join(SOURCE_DIR, "gettext"),
    freshenv=True,
    confoverrides={
        "gettext_additional_targets": [
            "index",
            "literal-block",
            "doctest-block",
            "raw",
            "image",
        ],
    },
)
def test_gettext_additional_targets(
    app,
    status,
    warning,
    get_sphinx_app_output,
    remove_sphinx_builds,
    file_regression,
):
    """Test gettext message extraction."""
    app.build()
    assert "build succeeded" in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert warnings == ""

    output = get_sphinx_app_output(app, filename="index.pot", buildername="gettext")
    output = re.sub(r"POT-Creation-Date: [0-9: +-]+", "POT-Creation-Date: ", output)
    output = re.sub(r"Copyright \(C\) [0-9]{4}", "Copyright (C) XXXX", output)

    file_regression.check(output, extension=f".sphinx{sphinx.version_info[0]}.pot")


@pytest.mark.sphinx(
    buildername="html", srcdir=os.path.join(SOURCE_DIR, "mathjax"), freshenv=True
)
def test_mathjax_warning(
    app,
    status,
    warning,
    remove_sphinx_builds,
):
    """Test mathjax config override warning."""
    app.build()
    assert "build succeeded" in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert (
        "overridden by myst-parser: 'other' -> 'tex2jax_process|mathjax_process|math|output_area'"
        in warnings
    )


@pytest.mark.sphinx(
    buildername="html",
    srcdir=os.path.join(SOURCE_DIR, "fieldlist"),
    freshenv=True,
)
def test_fieldlist_extension(
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
    assert warnings == ""

    try:
        get_sphinx_app_doctree(
            app,
            docname="index",
            regress=True,
            regress_ext=f".sphinx{sphinx.version_info[0]}.xml",
        )
    finally:
        get_sphinx_app_output(
            app,
            filename="index.html",
            regress_html=True,
            regress_ext=f".sphinx{sphinx.version_info[0]}.html",
        )
