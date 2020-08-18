import os
from pathlib import Path

import pytest

from markdown_it.utils import read_fixture_file
from myst_parser.docutils_renderer import make_document
from myst_parser.main import to_docutils


FIXTURE_PATH = Path(__file__).parent.joinpath("fixtures")


@pytest.mark.parametrize(
    "line,title,input,expected",
    read_fixture_file(FIXTURE_PATH.joinpath("mock_include.md")),
)
def test_render(line, title, input, expected, tmp_path):
    tmp_path.joinpath("other.md").write_text("a\nb\nc")
    tmp_path.joinpath("fmatter.md").write_text("---\na: 1\n---\nb")
    document = make_document(str(tmp_path / "test.md"))
    to_docutils(input, document=document, in_sphinx_env=True, srcdir=str(tmp_path))
    output = document.pformat().replace(str(tmp_path) + os.sep, "tmpdir" + "/").rstrip()
    print(output)
    assert output == expected.rstrip()


@pytest.mark.parametrize(
    "line,title,input,expected",
    read_fixture_file(FIXTURE_PATH.joinpath("mock_include_errors.md")),
)
def test_errors(line, title, input, expected, tmp_path):
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
    to_docutils(input, document=document, in_sphinx_env=True, srcdir=str(tmp_path))
    assert "\n".join(messages).rstrip() == expected.rstrip()
