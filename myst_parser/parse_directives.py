"""Module to parse fenced code blocks as directives.

Such a fenced code block starts with `{directive_name}`,
followed by arguments on the same line.

Directive options are read from a YAML block,
if the first content line starts with `---`, e.g.

::

    ```{directive_name} arguments
    ---
    option1: name
    option2: |
        Longer text block
    ---
    content...
    ```

Or the option block will be parsed if the first content line starts with `:`,
as a YAML block consisting of every line that starts with a `:`, e.g.

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
import re
from textwrap import dedent
from typing import Callable, Dict, Type

import yaml

from docutils.parsers.rst import Directive
from docutils.parsers.rst.directives.misc import TestDirective

from myst_parser.block_tokens import CodeFence


class DirectiveParsingError(Exception):
    pass


def parse_directive_text(
    directive_class: Type[Directive], content: str, token: CodeFence
):
    """See module docstring."""
    arguments = parse_directive_arguments(directive_class, token.arguments)
    body, options = parse_directive_options(content, directive_class)

    # remove first line if blank
    body_lines = body.splitlines()
    if body_lines and not body_lines[0].strip():
        body_lines = body_lines[1:]

    # check for body content
    if body_lines and not directive_class.has_content:
        raise DirectiveParsingError("No content permitted")

    return arguments, options, body_lines


def parse_directive_options(content: str, directive_class: Type[Directive]):
    options = {}
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

    if issubclass(directive_class, TestDirective):
        # technically this directive spec only accepts one option ('option')
        # but since its for testing only we accept all options
        return content, options

    # check options against spec
    options_spec = directive_class.option_spec  # type: Dict[str, Callable]
    for name, value in list(options.items()):
        convertor = options_spec.get(name, None)
        if convertor is None:
            raise DirectiveParsingError("Unknown option: {}".format(name))
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
