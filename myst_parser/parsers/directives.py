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

import re
from collections.abc import Callable
from dataclasses import dataclass
from textwrap import dedent
from typing import Any

import yaml
from docutils.parsers.rst import Directive
from docutils.parsers.rst.directives import flag
from docutils.parsers.rst.directives.misc import TestDirective
from docutils.parsers.rst.directives.tables import RSTTable
from docutils.parsers.rst.states import MarkupError

from myst_parser.warnings_ import MystWarnings

from .options import TokenizeError, options_to_tokens

YAML_LOAD_ERRORS = (yaml.YAMLError, ValueError, RecursionError)
"""Errors that ``yaml.safe_load`` can raise on invalid input:
``ValueError`` escapes PyYAML for some invalid scalars
(e.g. out-of-range timestamps like ``2021-99-99``),
and ``RecursionError`` for deeply nested data.
"""


@dataclass
class ParseWarnings:
    msg: str
    lineno: int | None = None
    type: MystWarnings = MystWarnings.DIRECTIVE_PARSING


@dataclass
class DirectiveParsingResult:
    arguments: list[str]
    """The arguments parsed from the first line.

    For ``table`` directives, this includes any caption lines that
    wrap onto the lines directly after the opening line (or the options block).
    """
    options: dict
    """Options parsed from the YAML block."""
    body: list[str]
    """The lines of body content"""
    body_offset: int
    """The number of lines from the directive's opening line
    to the first line of the body content.

    This is ``-1`` when body content starts on the opening line itself
    (only possible for directives that take no arguments).
    """
    warnings: list[ParseWarnings]
    """List of non-fatal errors encountered during parsing.
    (message, line_number)
    """


def parse_directive_text(
    directive_class: type[Directive],
    first_line: str,
    content: str,
    *,
    line: int | None = None,
    validate_options: bool = True,
    additional_options: dict[str, str] | None = None,
) -> DirectiveParsingResult:
    """Parse (and validate) the full directive text.

    :param first_line: The text on the same line as the directive name.
        May be an argument or body text, dependent on the directive
    :param content: All text after the first line. Can include options.
    :param validate_options: Whether to validate the values of options
        This is actually only here to be used by myst-nb cells,
        which converts options directly to JSON metadata, using the full YAML spec.
    :param additional_options: Additional options to add to the directive,
        above those parsed from the content (content options take priority).

    :raises MarkupError: if there is a fatal parsing/validation error
    """
    parse_warnings: list[ParseWarnings]
    options: dict[str, Any]
    body_lines: list[str]
    content_offset: int
    has_options_block: bool

    if directive_class.option_spec:
        # only look for an option block if there are possible options
        # body, options, option_errors = _parse_directive_options(
        result = _parse_directive_options(
            content,
            directive_class,
            line=line,
            as_yaml=not validate_options,
            additional_options=additional_options,
        )
        parse_warnings = result.warnings
        has_options_block = result.has_options
        options = result.options
        body_lines = result.content.splitlines()
        # Use the option-block line count directly rather than
        # ``len(content.splitlines()) - len(body_lines)``: re-splitting the
        # re-joined body drops a trailing blank line, which would otherwise
        # inflate the offset when the body ends in blank lines.
        content_offset = result.option_line_count
    else:
        parse_warnings = []
        has_options_block = False
        options = {}
        body_lines = content.splitlines()
        content_offset = 0

    if not (directive_class.required_arguments or directive_class.optional_arguments):
        # If there are no possible arguments, then the body can start on the argument line
        if first_line.strip():
            if has_options_block and any(body_lines):
                parse_warnings.append(
                    ParseWarnings(
                        "Splitting content across first line and body, "
                        "when an options block is present, is not recommended"
                    )
                )
            body_lines.insert(0, first_line)
            # the merged first body line sits on the opening line itself,
            # one line *before* where body content normally starts
            content_offset -= 1
        arguments = []
    else:
        arguments = parse_directive_arguments(directive_class, first_line)

    if issubclass(directive_class, RSTTable):
        # a ``{table}`` caption may wrap onto the lines directly below the
        # opening line (or the options block); this must run before the blank
        # line below is stripped, so that a separate paragraph is not folded
        arguments, body_lines, content_offset = _fold_table_caption_continuation(
            arguments,
            body_lines,
            content_offset,
            parse_warnings,
            None if line is None else line + 1,
        )

    # remove first line of body if blank
    # this is to allow space between the options and the content
    if body_lines and not body_lines[0].strip():
        body_lines = body_lines[1:]
        content_offset += 1

    # check for body content
    if body_lines and not directive_class.has_content:
        parse_warnings.append(ParseWarnings("Has content, but none permitted"))

    return DirectiveParsingResult(
        arguments, options, body_lines, content_offset, parse_warnings
    )


@dataclass
class _DirectiveOptions:
    content: str
    options: dict[str, Any]
    warnings: list[ParseWarnings]
    has_options: bool
    option_line_count: int
    """Number of source lines before the body (0 if there is no option block).

    This is the option block's own length, except when text trails a closing
    ``---``: that text is the first body line, so the closing line is not counted.
    It is derived before the body is joined back into a string, so it is not
    affected by trailing blank lines being lost in the ``"\\n".join(...)`` round-trip.
    """


def _parse_directive_options(
    content: str,
    directive_class: type[Directive],
    as_yaml: bool,
    line: int | None,
    additional_options: dict[str, str] | None = None,
) -> _DirectiveOptions:
    """Parse (and validate) the directive option section.

    :param content: All text after the directive's opening line,
        possibly starting with an option block
    :param directive_class: The directive class to validate options against
    :param as_yaml: Whether to parse the options block with the full YAML spec,
        rather than validating against the directive's option specification
        (used by myst-nb)
    :param line: The 1-based line number of the directive's opening line,
        or None if unknown
    :param additional_options: Additional options for the directive,
        which the options block takes priority over
    """
    options_block: str | None = None
    options_position: int | None = None
    """The 1-based source line of the first line of the options block."""
    option_line_count = 0
    """Number of source lines before the body, counted before the body is
    re-joined (so a body ending in blank lines does not throw the count off)."""
    if content.startswith("---"):
        options_position = None if line is None else line + 2
        content_lines = content.splitlines()[1:]
        for index, content_line in enumerate(content_lines):
            if content_line.startswith("---"):
                options_block = "\n".join(content_lines[:index])
                # any text after the closing delimiter's dashes becomes
                # the first line of the body content (and, being kept as
                # its own line, maps exactly to its source line)
                remainder = content_line.lstrip("-")
                remainder = remainder.removeprefix(" ")
                rest = content_lines[index + 1 :]
                content = "\n".join([remainder, *rest] if remainder else rest)
                # opening ``---`` + the option lines (``index``), then the
                # closing ``---``: normally the body starts on the next line
                # (``+ 2``), but when the closer carries trailing text, that text
                # is the first body line, on the closing line itself (``+ 1``).
                option_line_count = index + 1 if remainder else index + 2
                break
        else:
            options_block = "\n".join(content_lines)
            option_line_count = len(content.splitlines())
            content = ""
        options_block = dedent(options_block)
    elif content.lstrip().startswith(":"):
        options_position = None if line is None else line + 1
        content_lines = content.splitlines()
        yaml_lines = []
        while content_lines:
            stripped = content_lines[0].lstrip()
            # Stop at lines that don't start with a colon or have 3+ colons, which are colon fences
            # (e.g. nested directives like `::::{other}`)
            if not stripped.startswith(":") or stripped.startswith(":::"):
                break
            yaml_lines.append(content_lines.pop(0).lstrip()[1:])
        options_block = "\n".join(yaml_lines)
        option_line_count = len(yaml_lines)
        content = "\n".join(content_lines)

    has_options_block = options_block is not None

    if as_yaml:
        yaml_errors: list[ParseWarnings] = []
        try:
            yaml_options = yaml.safe_load(options_block or "") or {}
        except YAML_LOAD_ERRORS as exc:
            yaml_options = {}
            yaml_error_line = options_position
            if (
                options_position is not None
                and isinstance(exc, yaml.MarkedYAMLError)
                and exc.problem_mark is not None
            ):
                yaml_error_line = options_position + exc.problem_mark.line
            yaml_errors.append(
                ParseWarnings(
                    "Invalid options format (bad YAML)",
                    yaml_error_line,
                    MystWarnings.DIRECTIVE_OPTION,
                )
            )
        if not isinstance(yaml_options, dict):
            yaml_options = {}
            yaml_errors.append(
                ParseWarnings(
                    "Invalid options format (not a dict)",
                    options_position,
                    MystWarnings.DIRECTIVE_OPTION,
                )
            )
        return _DirectiveOptions(
            content, yaml_options, yaml_errors, has_options_block, option_line_count
        )

    validation_errors: list[ParseWarnings] = []

    options: dict[str, str] = {}
    option_lines: dict[str, int] = {}
    """0-based line of each key, within the options block
    (both block styles keep a 1:1 line correspondence with the source).
    """
    if options_block is not None:
        try:
            option_tokens, state = options_to_tokens(options_block)
        except TokenizeError as err:
            return _DirectiveOptions(
                content,
                options,
                [
                    ParseWarnings(
                        f"Invalid options format: {err.problem}",
                        None
                        if options_position is None
                        else options_position + err.problem_mark.line,
                        MystWarnings.DIRECTIVE_OPTION,
                    )
                ],
                has_options_block,
                option_line_count,
            )
        for key_token, value_token in option_tokens:
            options[key_token.value] = (
                value_token.value if value_token is not None else ""
            )
            option_lines[key_token.value] = key_token.start.line
        if state.has_comments:
            validation_errors.append(
                ParseWarnings(
                    "Directive options has # comments, which may not be supported in future versions.",
                    None
                    if options_position is None
                    else options_position
                    + (state.comment_lines[0] if state.comment_lines else 0),
                    MystWarnings.DIRECTIVE_OPTION_COMMENTS,
                )
            )

    def _option_line(name: str) -> int | None:
        """The 1-based source line of an option key, or None if unknown
        (e.g. keys injected via ``additional_options`` have no source line).
        """
        if options_position is None or name not in option_lines:
            return None
        return options_position + option_lines[name]

    if issubclass(directive_class, TestDirective):
        # technically this directive spec only accepts one option ('option')
        # but since its for testing only we accept all options
        return _DirectiveOptions(
            content, options, [], has_options_block, option_line_count
        )

    if additional_options:
        # The options block takes priority over additional options
        options = {**additional_options, **options}

    # check options against spec
    options_spec: dict[str, Callable] = directive_class.option_spec
    new_options: dict[str, Any] = {}
    value: str | None
    for name, value in options.items():
        try:
            converter = options_spec[name]
        except KeyError:
            validation_errors.append(
                ParseWarnings(
                    f"Unknown option key: {name!r} (allowed: {sorted(options_spec)})",
                    _option_line(name),
                    MystWarnings.DIRECTIVE_OPTION,
                )
            )
            continue
        if not value:
            # restructured text parses empty option values as None
            value = None
        if converter is flag:
            # flag will error if value is not empty,
            # but to be more permissive we allow any value
            value = None
        try:
            converted_value = converter(value)
        except (ValueError, TypeError) as error:
            validation_errors.append(
                ParseWarnings(
                    f"Invalid option value for {name!r}: {value}: {error}",
                    _option_line(name),
                    MystWarnings.DIRECTIVE_OPTION,
                )
            )
        else:
            new_options[name] = converted_value

    return _DirectiveOptions(
        content, new_options, validation_errors, has_options_block, option_line_count
    )


_TABLE_DELIMITER_ROW = re.compile(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$")
"""A GFM table delimiter row, e.g. ``|---|:--:|`` or ``--|--``."""

_OPTION_LIKE_LINE = re.compile(r"^(:[\w-]+:|---)")
"""A line that looks like the start of a directive option (or a YAML options block)."""

_NOT_CAPTION_TEXT = re.compile(
    r"^(```|~~~|:::|\$\$|\[[^\]]+\]:|%|\+\+\+|<!--|\(.*\)=\s*$)"
)
"""A line that starts a MyST block construct which is not caption text:
a code, directive or math fence, a link or footnote definition,
a comment, a block break, a target, or an HTML comment.
(Some of these render nothing, so may already precede a valid table.)"""


def _starts_table(lines: list[str], index: int) -> bool:
    """Return True if a GFM table starts at ``lines[index]``:
    a line containing ``|``, followed by a delimiter row.
    """
    return (
        index + 1 < len(lines)
        and "|" in lines[index]
        and _TABLE_DELIMITER_ROW.match(lines[index + 1]) is not None
    )


def _fold_table_caption_continuation(
    arguments: list[str],
    body_lines: list[str],
    content_offset: int,
    warnings: list[ParseWarnings],
    body_line: int | None,
) -> tuple[list[str], list[str], int]:
    """Join a wrapped ``{table}`` caption into the directive argument.

    MyST takes directive arguments from the opening line only, so a caption
    that wraps onto the next line(s) would otherwise become a leading paragraph
    in the body, and the table directive fails with "exactly one table expected".

    The lines are folded only if they directly follow the opening line
    (or the options block), with no blank line in between,
    and the first non-blank line after them starts a table.
    Anything else is left unchanged.

    :param arguments: The arguments parsed from the opening line
    :param body_lines: The body lines, before any leading blank line is stripped
    :param content_offset: The number of source lines between the line after
        the opening line and ``body_lines[0]`` (i.e. the options block's length)
    :param warnings: Parsing warnings, appended to in place
    :param body_line: The 1-based source line of the line after the opening line,
        or None if unknown
    :returns: The new ``(arguments, body_lines, content_offset)``
    """
    if not body_lines or not body_lines[0].strip():
        return arguments, body_lines, content_offset

    index = 0
    while (
        index < len(body_lines)
        and body_lines[index].strip()
        and not _starts_table(body_lines, index)
    ):
        index += 1
    caption_lines = [line.strip() for line in body_lines[:index]]
    table_start = index
    while table_start < len(body_lines) and not body_lines[table_start].strip():
        table_start += 1

    if not caption_lines or not _starts_table(body_lines, table_start):
        return arguments, body_lines, content_offset

    if any(_NOT_CAPTION_TEXT.match(line) for line in caption_lines):
        return arguments, body_lines, content_offset

    for line_index, caption_line in enumerate(caption_lines):
        if _OPTION_LIKE_LINE.match(caption_line):
            warnings.append(
                ParseWarnings(
                    "Options must directly follow the directive's opening line; "
                    "place wrapped caption lines after the options block",
                    None
                    if body_line is None
                    else body_line + content_offset + line_index,
                )
            )
            return arguments, body_lines, content_offset

    caption = " ".join(caption_lines)
    arguments = [f"{arguments[0].rstrip()} {caption}" if arguments else caption]
    return arguments, body_lines[table_start:], content_offset + table_start


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
