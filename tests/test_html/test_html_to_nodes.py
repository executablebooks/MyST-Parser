from pathlib import Path
from unittest.mock import Mock

import pytest
from docutils import nodes
from pytest_param_files import with_parameters

from myst_parser.html_to_nodes import html_to_nodes
from myst_parser.main import MdParserConfig

FIXTURE_PATH = Path(__file__).parent


@pytest.fixture()
def mock_renderer():
    def _run_directive(name: str, first_line: str, content: str, position: int):
        node = nodes.Element(name=name, first=first_line, position=position)
        node += nodes.Text(content)
        return [node]

    return Mock(
        md_config=MdParserConfig(enable_extensions=["html_image", "html_admonition"]),
        document={"source": "source"},
        reporter=Mock(
            warning=Mock(return_value=nodes.system_message("warning")),
            error=Mock(return_value=nodes.system_message("error")),
        ),
        run_directive=_run_directive,
    )


@with_parameters(FIXTURE_PATH / "html_to_nodes.md")
def test_html_to_nodes(file_params, mock_renderer):
    output = nodes.container()
    output += html_to_nodes(file_params.content, line_number=0, renderer=mock_renderer)
    file_params.assert_expected(output.pformat(), rstrip=True)
