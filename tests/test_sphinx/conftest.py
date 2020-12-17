"""
Uses sphinx's pytest fixture to run builds

usage:

.. code-block:: python

    @pytest.mark.sphinx(
        buildername='html',
        srcdir='path/to/source')
    def test_basic(app, status, warning, get_sphinx_app_output):

        app.build()

        assert 'build succeeded' in status.getvalue()  # Build succeeded
        warnings = warning.getvalue().strip()
        assert warnings == ""

        output = get_sphinx_app_output(app, buildername='html')

parameters available to parse to ``@pytest.mark.sphinx``:

- buildername='html'
- srcdir=None
- testroot='root' (only used if srcdir not set)
- freshenv=False
- confoverrides=None
- status=None
- warning=None
- tags=None
- docutilsconf=None

"""
import os
import pathlib
import shutil

import pytest
from sphinx.testing.path import path

SOURCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "sourcedirs"))


# TODO autouse not working, may need to be in root conftest
# (ideally _build folder should be in tempdir)
# @pytest.fixture(scope="session", autouse=True)
@pytest.fixture()
def remove_sphinx_builds():
    """remove all build directories from the test folder"""
    yield
    srcdirs = pathlib.Path(SOURCE_DIR)
    for entry in srcdirs.iterdir():  # type: pathlib.Path
        if entry.is_dir() and entry.joinpath("_build").exists():
            shutil.rmtree(str(entry.joinpath("_build")))


@pytest.fixture
def get_sphinx_app_output(file_regression):
    def read(
        app,
        buildername="html",
        filename="index.html",
        encoding="utf-8",
        extract_body=False,
        remove_scripts=False,
        regress_html=False,
        replace=None,
    ):

        outpath = path(os.path.join(str(app.srcdir), "_build", buildername, filename))
        if not outpath.exists():
            raise IOError("no output file exists: {}".format(outpath))

        try:
            # introduced in sphinx 3.0
            content = outpath.read_text(encoding=encoding)
        except AttributeError:
            content = outpath.text(encoding=encoding)

        if regress_html:
            # only regress the inner body, since other sections are non-deterministic
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(content, "html.parser")
            doc_div = soup.findAll("div", {"class": "documentwrapper"})[0]
            text = doc_div.prettify()
            for find, rep in (replace or {}).items():
                text = text.replace(find, rep)
            file_regression.check(text, extension=".html", encoding="utf8")

        return content

    return read


@pytest.fixture
def get_sphinx_app_doctree(file_regression):
    def read(app, docname="index", resolve=False, regress=False, replace=None):
        if resolve:
            doctree = app.env.get_and_resolve_doctree(docname, app.builder)
            extension = ".resolved.xml"
        else:
            doctree = app.env.get_doctree(docname)
            extension = ".xml"

        # convert absolute filenames
        for node in doctree.traverse(
            lambda n: "source" in n and not isinstance(n, str)
        ):
            node["source"] = pathlib.Path(node["source"]).name

        if regress:
            text = doctree.pformat()  # type: str
            for find, rep in (replace or {}).items():
                text = text.replace(find, rep)
            file_regression.check(text, extension=extension)

        return doctree

    return read
