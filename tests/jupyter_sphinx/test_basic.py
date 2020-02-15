from collections import namedtuple
from io import StringIO
import os

import pytest
from sphinx.testing.util import path

SOURCE_PATH = path(os.path.realpath(os.path.dirname(__file__))) / "sourcedirs"
BuildResult = namedtuple("BuildResult", ["app", "doctrees"])


@pytest.fixture(scope="function")
def build_sphinx(tmp_path, make_app):
    def _build_doctree(
        srcfolder,
        confoverrides=None,
        file_names=("contents",),
        buildername="html",
        assert_succeeded=True,
        in_temp=True,
    ):
        srcdir = SOURCE_PATH / srcfolder
        if in_temp:
            srcdir.copytree(str(tmp_path / "srcdir"))
            srcdir = path(str(tmp_path / "srcdir"))
        if not (srcdir / "conf.py").exists():
            (srcdir / "conf.py").write_text(
                "extensions = ['jupyter_sphinx']\nmaster_doc = 'contents'"
            )
        status, warning = StringIO(), StringIO()
        app = make_app(
            srcdir=srcdir,
            buildername=buildername,
            confoverrides=confoverrides,
            freshenv=True,
            status=status,
            warning=warning,
        )
        app.build()
        if assert_succeeded:
            assert "build succeeded" in status.getvalue()
            warnings = warning.getvalue().strip()
            assert warnings == ""
        doctrees = {}
        for file_name in file_names:
            doctree = app.env.get_doctree(file_name)
            doctree.document["source"] = "<source_path>"
            doctrees[file_name] = doctree
        return BuildResult(app, doctrees)

    return _build_doctree


def test_basic(build_sphinx, file_regression, data_regression):
    result = build_sphinx("basic", in_temp=True)
    file_regression.check(result.doctrees["contents"].pformat(), extension=".xml")
    cache_data = result.app.env.jupyter_db.to_dict(
        drop_columns=("created_at", "updated_at")
    )
    data_regression.check(cache_data)
