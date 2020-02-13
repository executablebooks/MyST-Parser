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

# import pathlib
# import shutil
import re

import pytest
from sphinx.testing.path import path


# @pytest.fixture(scope="session", autouse=True)
# def remove_sphinx_builds():
#     """ remove all build directories from the test folder
#     """
#     srcdirs = pathlib.Path(get_test_source_dir())
#     for entry in srcdirs.iterdir():  # type: pathlib.Path
#         if entry.is_dir() and entry.joinpath("_build").exists():
#             shutil.rmtree(str(entry.joinpath("_build")))


@pytest.fixture
def get_sphinx_app_output():
    def read(
        app,
        buildername="html",
        filename="index.html",
        encoding="utf-8",
        extract_body=False,
        remove_scripts=False,
    ):

        outpath = path(os.path.join(str(app.srcdir), "_build", buildername, filename))
        if not outpath.exists():
            raise IOError("no output file exists: {}".format(outpath))

        content = outpath.text(encoding=encoding)

        if extract_body:
            body_rgx = re.compile("\\<body\\>(.*)\\</body\\>", re.DOTALL)
            body_search = body_rgx.search(content)
            if not body_search:
                raise IOError("could not find body content of {}".format(path))
            content = body_search.group(1)

        if remove_scripts:
            # remove script environments which can change
            script_rgx = re.compile("\\<script\\>(.*)\\</script\\>", re.DOTALL)
            content = script_rgx.sub("<script></script>", content)

        return content

    return read
