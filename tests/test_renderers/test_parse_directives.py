# TODO add more tests
import pytest

from docutils.parsers.rst.directives.admonitions import Note
from docutils.parsers.rst.directives.body import Rubric

from myst_parser.parse_directives import parse_directive_text, DirectiveParsingError


@pytest.mark.parametrize("klass,arguments,content", [(Note, "", "a"), (Note, "a", "")])
def test_parsing(klass, arguments, content, data_regression):
    arguments, options, body_lines = parse_directive_text(klass, arguments, content)
    data_regression.check(
        {"arguments": arguments, "options": options, "body": body_lines}
    )


@pytest.mark.parametrize(
    "descript,klass,arguments,content", [("no content", Rubric, "", "a")]
)
def test_parsing_errors(descript, klass, arguments, content):
    with pytest.raises(DirectiveParsingError):
        parse_directive_text(klass, arguments, content)
