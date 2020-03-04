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
import pickle
import shutil

from docutils.nodes import document
import pytest
from sphinx.testing.path import path

SOURCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "sourcedirs"))


# TODO autouse not working, may need to be in root conftest
# (ideally _build folder should be in tempdir)
# @pytest.fixture(scope="session", autouse=True)
@pytest.fixture()
def remove_sphinx_builds():
    """ remove all build directories from the test folder
    """
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
    ):

        outpath = path(os.path.join(str(app.srcdir), "_build", buildername, filename))
        if not outpath.exists():
            raise IOError("no output file exists: {}".format(outpath))

        content = outpath.text(encoding=encoding)

        if regress_html:
            # only regress the inner body, since other sections are non-deterministic
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(content, "html.parser")
            doc_div = soup.findAll("div", {"class": "documentwrapper"})[0]
            file_regression.check(doc_div.prettify(), extension=".html")

        return content

    return read


@pytest.fixture
def get_sphinx_app_doctree(file_regression):
    def read(
        app,
        filename="index.doctree",
        folder="doctrees",
        encoding="utf-8",
        regress=False,
    ):

        outpath = path(os.path.join(str(app.srcdir), "_build", folder, filename))
        if not outpath.exists():
            raise IOError("no output file exists: {}".format(outpath))

        with open(outpath, "rb") as handle:
            doctree = pickle.load(handle)  # type: document

        # convert absolute filenames
        for node in doctree.traverse(lambda n: "source" in n):
            node["source"] = pathlib.Path(node["source"]).name

        if regress:
            file_regression.check(doctree.pformat(), extension=".xml")

        return doctree

    return read
