import re
from threading import local

from mistletoe import span_token, core_tokens
from mistletoe.span_token import (  # noqa F401
    HTMLSpan,
    Emphasis,
    EscapeSequence,
    AutoLink,
    Image,
    InlineCode,
    LineBreak,
    Link,
    RawText,
    Strong,
)

"""
Tokens to be included in the parsing process, in the order specified.
RawText is last as a 'fallback' token
"""
__all__ = (
    "Role",
    "HTMLSpan",
    "EscapeSequence",
    "AutoLink",
    "Target",
    "CoreTokens",
    "Math",
    "InlineCode",
    "LineBreak",
    "RawText",
)
# Note Strikethrough is left out from the core mistletoe tokens,
# since there is no matching element in docutils


class CoreTokens(span_token.SpanToken):
    precedence = 3

    def __new__(self, match):
        return globals()[match.type](match)

    @classmethod
    def find(cls, string):
        return find_core_tokens(string, span_token._root_node)


class Role(span_token.SpanToken):
    """
    Inline role tokens. ("{name}`some code`")
    """

    pattern = re.compile(
        r"(?<!\\|`)(?:\\\\)*{([\:\-\_0-9a-zA-A]*)}(`+)(?!`)(.+?)(?<!`)\2(?!`)",
        re.DOTALL,
    )
    parse_inner = False
    # precedence = 6  # higher precedence than InlineCode?

    def __init__(self, match):
        self.name = match.group(1)
        content = match.group(3)
        self.children = (
            span_token.RawText(" ".join(re.split("[ \n]+", content.strip()))),
        )


class Math(span_token.SpanToken):
    parse_inner = False
    parse_group = 0
    precedence = 2

    @classmethod
    def find(cls, string):
        matches = _math_matches.value[:]
        _math_matches.value = []
        return matches


class Target(span_token.SpanToken):
    """Target tokens. ("(target name)")"""

    pattern = re.compile(r"(?<!\\)(?:\\\\)*\((.+?)\)\=", re.DOTALL)
    parse_inner = False

    def __init__(self, match):
        content = match.group(self.parse_group)
        self.children = (RawText(content),)
        self.target = content


math_pattern = re.compile(r"(?<!\\)(?:\\\\)*(\${1,2})([^\$]+?)\1")
_math_matches = local()
_math_matches.value = []


def find_core_tokens(string, root):
    matches = []
    # escaped denotes that the last cursor position had `\`
    escaped = False
    # delimiter runs are sequences of `*` or `_`
    in_delimiter_run = None
    delimiters = []
    in_image = False
    start = 0

    def _advance_block_regexes(_cursor):
        _next_code_match = core_tokens.code_pattern.search(string, _cursor)
        _next_math_match = math_pattern.search(string, _cursor)
        return _cursor, _next_code_match, _next_math_match

    i, next_code_match, next_math_match = _advance_block_regexes(0)
    while i < len(string):
        # If a code block starts here, record it and advance the cursor
        if next_code_match is not None and i == next_code_match.start():
            core_tokens._code_matches.append(next_code_match)
            # advance the cursor and re-compute next blocks
            i, next_code_match, next_math_match = _advance_block_regexes(
                next_code_match.end()
            )
            continue
        # If a math block starts here, record it and advance the cursor
        if next_math_match is not None and i == next_math_match.start():
            if in_delimiter_run:
                delimiters.append(core_tokens.Delimiter(start, i, string))
            in_delimiter_run = None
            _math_matches.value.append(next_math_match)
            # advance the cursor and re-compute next blocks
            i, next_code_match, next_math_match = _advance_block_regexes(
                next_math_match.end()
            )
            continue
        c = string[i]
        # if the cursor position is escaped, record and advance
        if c == "\\" and not escaped:
            escaped = True
            i += 1
            continue
        # if the cursor reaches the end of a delimiter run,
        # record the delimiter and reset
        if in_delimiter_run is not None and (c != in_delimiter_run or escaped):
            delimiters.append(
                core_tokens.Delimiter(start, i if not escaped else i - 1, string)
            )
            in_delimiter_run = None
        # if the cursor reaches a new delimiter, start a delimiter run
        if in_delimiter_run is None and (c in {"*", "_"}) and not escaped:
            in_delimiter_run = c
            start = i
        if not escaped:
            if c == "[":
                if not in_image:
                    delimiters.append(core_tokens.Delimiter(i, i + 1, string))
                else:
                    delimiters.append(core_tokens.Delimiter(i - 1, i + 1, string))
                    in_image = False
            elif c == "!":
                in_image = True
            elif c == "]":
                i = core_tokens.find_link_image(string, i, delimiters, matches, root)
                i, next_code_match, next_math_match = _advance_block_regexes(i)
            elif in_image:
                in_image = False
        else:
            escaped = False
        i += 1
    if in_delimiter_run:
        delimiters.append(core_tokens.Delimiter(start, i, string))
    core_tokens.process_emphasis(string, None, delimiters, matches)
    return matches
