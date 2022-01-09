import os
from pathlib import Path

import pytest
from pytest_param_files import with_parameters

from myst_parser.docutils_renderer import make_document
from myst_parser.main import to_docutils

FIXTURE_PATH = Path(__file__).parent.joinpath("fixtures")


@with_parameters(FIXTURE_PATH / "mock_include.md")
def test_render(file_params, tmp_path):
    tmp_path.joinpath("other.md").write_text("a\nb\nc")
    tmp_path.joinpath("fmatter.md").write_text("---\na: 1\n---\nb")
    document = make_document(str(tmp_path / "test.md"))
    to_docutils(
        file_params.content, document=document, in_sphinx_env=True, srcdir=str(tmp_path)
    )
    output = document.pformat().replace(str(tmp_path) + os.sep, "tmpdir" + "/").rstrip()
    file_params.assert_expected(output, rstrip=True)


@with_parameters(FIXTURE_PATH / "mock_include_errors.md")
def test_errors(file_params, tmp_path):
    if file_params.title.startswith("Non-existent path") and os.name == "nt":
        pytest.skip("tmp_path not converted correctly on Windows")

    tmp_path.joinpath("bad.md").write_text("{a}`b`")
    document = make_document(str(tmp_path / "test.md"))
    messages = []

    def observer(msg_node):
        if msg_node["level"] > 1:
            messages.append(
                msg_node.astext().replace(str(tmp_path) + os.sep, "tmpdir" + "/")
            )

    document.reporter.attach_observer(observer)
    document.reporter.halt_level = 6
    to_docutils(
        file_params.content, document=document, in_sphinx_env=True, srcdir=str(tmp_path)
    )
    file_params.assert_expected("\n".join(messages), rstrip=True)
