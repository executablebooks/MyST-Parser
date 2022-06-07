from pathlib import Path

import pytest
import yaml
from docutils.parsers.rst.directives.admonitions import Admonition, Note
from docutils.parsers.rst.directives.body import Rubric
from markdown_it import MarkdownIt

from myst_parser.parsers.directives import DirectiveParsingError, parse_directive_text

FIXTURE_PATH = Path(__file__).parent.joinpath("fixtures")


@pytest.mark.param_file(FIXTURE_PATH / "directive_parsing.txt")
def test_parsing(file_params):
    """Test parsing of directive text."""
    tokens = MarkdownIt("commonmark").parse(file_params.content)
    assert len(tokens) == 1 and tokens[0].type == "fence"
    name, *first_line = tokens[0].info.split(maxsplit=1)
    if name == "{note}":
        klass = Note
    elif name == "{admonition}":
        klass = Admonition
    else:
        raise AssertionError(f"Unknown directive: {name}")
    arguments, options, body_lines, content_offset = parse_directive_text(
        klass, first_line[0] if first_line else "", tokens[0].content
    )
    outcome = yaml.safe_dump(
        {
            "arguments": arguments,
            "options": options,
            "body": body_lines,
            "content_offset": content_offset,
        },
        sort_keys=True,
    )
    file_params.assert_expected(outcome, rstrip_lines=True)


@pytest.mark.parametrize(
    "descript,klass,arguments,content", [("no content", Rubric, "", "a")]
)
def test_parsing_errors(descript, klass, arguments, content):
    with pytest.raises(DirectiveParsingError):
        parse_directive_text(klass, arguments, content)
