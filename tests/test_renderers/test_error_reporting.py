from pathlib import Path

import pytest

from markdown_it.utils import read_fixture_file
from myst_parser.docutils_renderer import make_document
from myst_parser.main import to_docutils, MdParserConfig


FIXTURE_PATH = Path(__file__).parent.joinpath("fixtures")


@pytest.mark.parametrize(
    "line,title,input,expected",
    read_fixture_file(FIXTURE_PATH.joinpath("reporter_warnings.md")),
    ids=[
        f"{i[0]}-{i[1]}"
        for i in read_fixture_file(FIXTURE_PATH / "reporter_warnings.md")
    ],
)
def test_basic(line, title, input, expected):
    document = make_document("source/path")
    messages = []

    def observer(msg_node):
        if msg_node["level"] > 1:
            messages.append(msg_node.astext())

    document.reporter.attach_observer(observer)
    to_docutils(input, MdParserConfig(renderer="docutils"), document=document)
    assert "\n".join(messages).rstrip() == expected.rstrip()
