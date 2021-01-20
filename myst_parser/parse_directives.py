"""Fenced code blocks are parsed as directives,
if the block starts with ``{directive_name}``,
followed by arguments on the same line.

Directive options are read from a YAML block,
if the first content line starts with ``---``, e.g.

::

    ```{directive_name} arguments
    ---
    option1: name
    option2: |
        Longer text block
    ---
    content...
    ```

Or the option block will be parsed if the first content line starts with ``:``,
as a YAML block consisting of every line that starts with a ``:``, e.g.

::

    ```{directive_name} arguments
    :option1: name
    :option2: other

    content...
    ```

If the first line of a directive's content is blank, this will be stripped
from the content.
This is to allow for separation between the option block and content.

"""
import datetime
import re
from textwrap import dedent
from typing import Any, Callable, Dict, Type

import yaml
from docutils.parsers.rst import Directive
from docutils.parsers.rst.directives.misc import TestDirective


class DirectiveParsingError(Exception):
    """Raise on parsing/validation error."""

    pass


def parse_directive_text(
    directive_class: Type[Directive],
    first_line: str,
    content: str,
    validate_options: bool = True,
):
    """Parse (and validate) the full directive text.

    :param first_line: The text on the same line as the directive name.
        May be an argument or body text, dependent on the directive
    :param content: All text after the first line. Can include options.
    :param validate_options: Whether to validate the values of options

    """
    if directive_class.option_spec:
        body, options = parse_directive_options(
            content, directive_class, validate=validate_options
        )
    else:
        # If there are no possible options, we do not look for a YAML block
        options = {}
        body = content

    body_lines = body.splitlines()

    if not (
        directive_class.required_arguments
        or directive_class.optional_arguments
        or options
    ):
        # If there are no possible arguments and no option block,
        # then the body starts on the argument line
        if first_line:
            body_lines.insert(0, first_line)
        arguments = []
    else:
        arguments = parse_directive_arguments(directive_class, first_line)

    # remove first line of body if blank
    # this is to allow space between the options and the content
    if body_lines and not body_lines[0].strip():
        body_lines = body_lines[1:]

    # check for body content
    if body_lines and not directive_class.has_content:
        raise DirectiveParsingError("No content permitted")

    return arguments, options, body_lines


def parse_directive_options(
    content: str, directive_class: Type[Directive], validate: bool = True
):
    """Parse (and validate) the directive option section."""
    options: Dict[str, Any] = {}
    if content.startswith("---"):
        content = "\n".join(content.splitlines()[1:])
        match = re.search(r"^-{3,}", content, re.MULTILINE)
        if match:
            yaml_block = content[: match.start()]
            content = content[match.end() + 1 :]  # TODO advance line number
        else:
            yaml_block = content
            content = ""
        yaml_block = dedent(yaml_block)
        try:
            options = yaml.safe_load(yaml_block) or {}
        except (yaml.parser.ParserError, yaml.scanner.ScannerError) as error:
            raise DirectiveParsingError("Invalid options YAML: " + str(error))
    elif content.lstrip().startswith(":"):
        content_lines = content.splitlines()  # type: list
        yaml_lines = []
        while content_lines:
            if not content_lines[0].lstrip().startswith(":"):
                break
            yaml_lines.append(content_lines.pop(0).lstrip()[1:])
        yaml_block = "\n".join(yaml_lines)
        content = "\n".join(content_lines)
        try:
            options = yaml.safe_load(yaml_block) or {}
        except (yaml.parser.ParserError, yaml.scanner.ScannerError) as error:
            raise DirectiveParsingError("Invalid options YAML: " + str(error))
        if not isinstance(options, dict):
            raise DirectiveParsingError(f"Invalid options (not dict): {options}")

    if (not validate) or issubclass(directive_class, TestDirective):
        # technically this directive spec only accepts one option ('option')
        # but since its for testing only we accept all options
        return content, options

    # check options against spec
    options_spec = directive_class.option_spec  # type: Dict[str, Callable]
    for name, value in list(options.items()):
        convertor = options_spec.get(name, None)
        if convertor is None:
            raise DirectiveParsingError(f"Unknown option: {name}")
        if not isinstance(value, str):
            if value is True or value is None:
                value = ""  # flag converter requires no argument
            elif isinstance(value, (int, float, datetime.date, datetime.datetime)):
                # convertor always requires string input
                value = str(value)
            else:
                raise DirectiveParsingError(
                    f'option "{name}" value not string (enclose with ""): {value}'
                )
        try:
            converted_value = convertor(value)
        except (ValueError, TypeError) as error:
            raise DirectiveParsingError(
                "Invalid option value: (option: '{}'; value: {})\n{}".format(
                    name, value, error
                )
            )
        options[name] = converted_value

    return content, options


def parse_directive_arguments(directive, arg_text):
    """Parse (and validate) the directive argument section."""
    required = directive.required_arguments
    optional = directive.optional_arguments
    arguments = arg_text.split()
    if len(arguments) < required:
        raise DirectiveParsingError(
            "{} argument(s) required, {} supplied".format(required, len(arguments))
        )
    elif len(arguments) > required + optional:
        if directive.final_argument_whitespace:
            arguments = arg_text.split(None, required + optional - 1)
        else:
            raise DirectiveParsingError(
                "maximum {} argument(s) allowed, {} supplied".format(
                    required + optional, len(arguments)
                )
            )
    return arguments
