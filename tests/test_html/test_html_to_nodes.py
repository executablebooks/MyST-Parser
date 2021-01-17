from pathlib import Path
from unittest.mock import Mock

from docutils import nodes
import pytest

from markdown_it.utils import read_fixture_file
from myst_parser.html_to_nodes import html_to_nodes


FIXTURE_PATH = Path(__file__).parent


@pytest.fixture()
def mock_renderer():
    def _run_directive(name: str, first_line: str, content: str, position: int):
        node = nodes.Element(name=name, first=first_line, position=position)
        node += nodes.Text(content)
        return [node]

    return Mock(
        config={"enable_html_img": True, "enable_html_admonition": True},
        document={"source": "source"},
        reporter=Mock(
            warning=Mock(return_value=nodes.system_message("warning")),
            error=Mock(return_value=nodes.system_message("error")),
        ),
        run_directive=_run_directive,
    )


@pytest.mark.parametrize(
    "line,title,text,expected",
    read_fixture_file(FIXTURE_PATH / "html_to_nodes.md"),
    ids=[
        f"{i[0]}-{i[1]}" for i in read_fixture_file(FIXTURE_PATH / "html_to_nodes.md")
    ],
)
def test_html_to_nodes(line, title, text, expected, mock_renderer):
    output = nodes.container()
    output += html_to_nodes(text, line_number=0, renderer=mock_renderer)
    try:
        assert output.pformat().rstrip() == expected.rstrip()
    except AssertionError:
        print(output.pformat())
        raise
