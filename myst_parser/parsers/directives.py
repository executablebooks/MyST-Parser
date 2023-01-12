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
from __future__ import annotations

import datetime
import re
from dataclasses import dataclass
from textwrap import dedent
from typing import Any, Callable

import yaml
from docutils.parsers.rst import Directive
from docutils.parsers.rst.directives.misc import TestDirective
from docutils.parsers.rst.states import MarkupError


@dataclass
class DirectiveParsingResult:
    arguments: list[str]
    """The arguments parsed from the first line."""
    options: dict
    """Options parsed from the YAML block."""
    body: list[str]
    """The lines of body content"""
    body_offset: int
    """The number of lines to the start of the body content."""
    warnings: list[str]
    """List of non-fatal errors encountered during parsing."""


def parse_directive_text(
    directive_class: type[Directive],
    first_line: str,
    content: str,
    validate_options: bool = True,
) -> DirectiveParsingResult:
    """Parse (and validate) the full directive text.

    :param first_line: The text on the same line as the directive name.
        May be an argument or body text, dependent on the directive
    :param content: All text after the first line. Can include options.
    :param validate_options: Whether to validate the values of options

    :raises MarkupError: if there is a fatal parsing/validation error
    """
    parse_errors: list[str] = []
    if directive_class.option_spec:
        body, options, option_errors = parse_directive_options(
            content, directive_class, validate=validate_options
        )
        parse_errors.extend(option_errors)
        body_lines = body.splitlines()
        content_offset = len(content.splitlines()) - len(body_lines)
    else:
        # If there are no possible options, we do not look for a YAML block
        options = {}
        body_lines = content.splitlines()
        content_offset = 0

    if not (directive_class.required_arguments or directive_class.optional_arguments):
        # If there are no possible arguments, then the body starts on the argument line
        if first_line:
            body_lines.insert(0, first_line)
        arguments = []
    else:
        arguments = parse_directive_arguments(directive_class, first_line)

    # remove first line of body if blank
    # this is to allow space between the options and the content
    if body_lines and not body_lines[0].strip():
        body_lines = body_lines[1:]
        content_offset += 1

    # check for body content
    if body_lines and not directive_class.has_content:
        parse_errors.append("Has content, but none permitted")

    return DirectiveParsingResult(
        arguments, options, body_lines, content_offset, parse_errors
    )


def parse_directive_options(
    content: str, directive_class: type[Directive], validate: bool = True
) -> tuple[str, dict, list[str]]:
    """Parse (and validate) the directive option section.

    :returns: (content, options, validation_errors)
    """
    options: dict[str, Any] = {}
    validation_errors: list[str] = []
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
        except (yaml.parser.ParserError, yaml.scanner.ScannerError):
            validation_errors.append("Invalid options format (bad YAML)")
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
        except (yaml.parser.ParserError, yaml.scanner.ScannerError):
            validation_errors.append("Invalid options format (bad YAML)")

    if not isinstance(options, dict):
        options = {}
        validation_errors.append("Invalid options format (not a dict)")

    if validation_errors:
        return content, options, validation_errors

    if (not validate) or issubclass(directive_class, TestDirective):
        # technically this directive spec only accepts one option ('option')
        # but since its for testing only we accept all options
        return content, options, validation_errors

    # check options against spec
    options_spec: dict[str, Callable] = directive_class.option_spec
    unknown_options: list[str] = []
    new_options: dict[str, Any] = {}
    for name, value in options.items():
        try:
            convertor = options_spec[name]
        except KeyError:
            unknown_options.append(name)
            continue
        if not isinstance(value, str):
            if value is True or value is None:
                value = None  # flag converter requires no argument
            elif isinstance(value, (int, float, datetime.date, datetime.datetime)):
                # convertor always requires string input
                value = str(value)
            else:
                validation_errors.append(
                    f'option "{name}" value not string (enclose with ""): {value}'
                )
                continue
        try:
            converted_value = convertor(value)
        except (ValueError, TypeError) as error:
            validation_errors.append(
                f"Invalid option value for {name!r}: {value}: {error}"
            )
        else:
            new_options[name] = converted_value

    if unknown_options:
        validation_errors.append(
            f"Unknown option keys: {sorted(unknown_options)} "
            f"(allowed: {sorted(options_spec)})"
        )

    return content, new_options, validation_errors


def parse_directive_arguments(
    directive_cls: type[Directive], arg_text: str
) -> list[str]:
    """Parse (and validate) the directive argument section."""
    required = directive_cls.required_arguments
    optional = directive_cls.optional_arguments
    arguments = arg_text.split()
    if len(arguments) < required:
        raise MarkupError(f"{required} argument(s) required, {len(arguments)} supplied")
    elif len(arguments) > required + optional:
        if directive_cls.final_argument_whitespace:
            arguments = arg_text.split(None, required + optional - 1)
        else:
            raise MarkupError(
                f"maximum {required + optional} argument(s) allowed, "
                f"{len(arguments)} supplied"
            )
    return arguments
