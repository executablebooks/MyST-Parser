from html import escape
from io import StringIO
from pathlib import Path
from unittest.mock import Mock

import pytest
from docutils import nodes
from docutils.core import publish_doctree

from myst_parser.config.main import MdParserConfig
from myst_parser.mdit_to_docutils.html_to_nodes import html_to_nodes
from myst_parser.parsers.docutils_ import Parser

FIXTURE_PATH = Path(__file__).parent


@pytest.fixture()
def mock_renderer():
    def _run_directive(
        name: str,
        first_line: str,
        content: str,
        position: int,
        additional_options: dict[str, str] | None = None,
    ) -> list[nodes.Element]:
        node = nodes.Element(name=name, first=first_line, position=position)
        if additional_options:
            # Display options in the same format as the content-based fixtures.
            content = "\n".join(f":{k}: {v}" for k, v in additional_options.items())
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


@pytest.mark.param_file(FIXTURE_PATH / "html_to_nodes.md")
def test_html_to_nodes(file_params, mock_renderer, normalize_doctree_xml):
    output = nodes.container()
    output += html_to_nodes(file_params.content, line_number=0, renderer=mock_renderer)
    file_params.assert_expected(normalize_doctree_xml(output.pformat()), rstrip=True)


@pytest.mark.parametrize(
    "alt",
    ["ordinary text", "A # sign", '"quoted" text', "First\nsecond", "  padded text  "],
)
@pytest.mark.parametrize("inline", [False, True])
def test_html_image_literal_alt(alt: str, inline: bool) -> None:
    """HTML attributes must not be interpreted as directive option syntax."""
    image = f'<img src="example.png" alt="{escape(alt, quote=True)}">'
    source = f"before {image} after\n" if inline else f"{image}\n"
    warnings = StringIO()
    document = publish_doctree(
        source,
        parser=Parser(),
        settings_overrides={
            "myst_enable_extensions": ["html_image"],
            "warning_stream": warnings,
        },
    )
    images = list(document.findall(nodes.image))
    assert len(images) == 1
    assert images[0]["alt"] == alt
    assert warnings.getvalue() == ""


@pytest.mark.parametrize(
    ("width", "height"),
    [(" 200 ", " 100 "), ("\t200px\t", "\t100px\t"), (" 50% ", " 2em ")],
)
@pytest.mark.parametrize("inline", [False, True])
def test_html_image_padded_dimensions(width: str, height: str, inline: bool) -> None:
    """Dimension values retain the whitespace normalization of directive options."""
    image = f"<img src='x.png' width='{width}' height='{height}'>"
    source = f"before {image} after\n" if inline else f"{image}\n"
    warnings = StringIO()
    document = publish_doctree(
        source,
        parser=Parser(),
        settings_overrides={
            "myst_enable_extensions": ["html_image"],
            "warning_stream": warnings,
        },
    )
    images = list(document.findall(nodes.image))
    assert len(images) == 1
    assert warnings.getvalue() == ""
    assert images[0]["width"] == width.strip()
    assert images[0]["height"] == height.strip()


@pytest.mark.parametrize("dimension", ["width", "height"])
@pytest.mark.parametrize("inline", [False, True])
def test_html_image_invalid_dimension(dimension: str, inline: bool) -> None:
    """Normalizing whitespace must not bypass dimension validation."""
    image = f"<img src='x.png' {dimension}=' invalid '>"
    source = f"before {image} after\n" if inline else f"{image}\n"
    warnings = StringIO()
    document = publish_doctree(
        source,
        parser=Parser(),
        settings_overrides={
            "myst_enable_extensions": ["html_image"],
            "warning_stream": warnings,
        },
    )
    images = list(document.findall(nodes.image))
    assert len(images) == 1
    assert dimension not in images[0]
    assert f"Invalid option value for '{dimension}'" in warnings.getvalue()
    assert "[myst.directive_option]" in warnings.getvalue()
