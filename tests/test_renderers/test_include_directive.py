import os
from io import StringIO
from pathlib import Path

import pytest
from docutils.core import publish_doctree

from myst_parser.parsers.docutils_ import Parser

FIXTURE_PATH = Path(__file__).parent.joinpath("fixtures")


@pytest.mark.param_file(FIXTURE_PATH / "mock_include.md")
def test_render(file_params, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    tmp_path.joinpath("other.md").write_text("a\nb\nc")
    tmp_path.joinpath("fmatter.md").write_text("---\na: 1\n---\nb")

    doctree = publish_doctree(
        file_params.content,
        parser=Parser(),
        settings_overrides={"myst_highlight_code_blocks": False},
    )

    doctree["source"] = "tmpdir/test.md"
    if file_params.title.startswith("Include code:"):
        # from sphinx 5.3 whitespace nodes are now present
        for node in doctree.traverse():
            if node.tagname == "inline" and node["classes"] == ["whitespace"]:
                node.parent.remove(node)
    output = doctree.pformat().replace(str(tmp_path) + os.sep, "tmpdir/").rstrip()

    file_params.assert_expected(output, rstrip=True)


@pytest.mark.param_file(FIXTURE_PATH / "mock_include_errors.md")
def test_errors(file_params, tmp_path, monkeypatch):
    if file_params.title.startswith("Non-existent path") and os.name == "nt":
        pytest.skip("tmp_path not converted correctly on Windows")

    monkeypatch.chdir(tmp_path)

    tmp_path.joinpath("bad.md").write_text("{a}`b`")

    report_stream = StringIO()
    publish_doctree(
        file_params.content,
        source_path=str(tmp_path / "test.md"),
        parser=Parser(),
        settings_overrides={"halt_level": 6, "warning_stream": report_stream},
    )

    file_params.assert_expected(
        report_stream.getvalue().replace(str(tmp_path) + os.sep, "tmpdir/"),
        rstrip=True,
    )
