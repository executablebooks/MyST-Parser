import re
from threading import local

from mistletoe import span_token, core_tokens
from mistletoe.span_token import (  # noqa F401
    HTMLSpan,
    Emphasis,
    EscapeSequence,
    AutoLink,
    Image,
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


_core_matches = local()
_core_matches.value = {}


class CoreTokens(span_token.SpanToken):
    precedence = 3

    def __new__(self, match):
        return globals()[match.type](match)

    @classmethod
    def find(cls, string):
        return find_core_tokens(string, span_token._root_node)


class InlineCode(span_token.InlineCode):
    @classmethod
    def find(cls, string):
        return _core_matches.value.pop("InlineCode", [])


class Role(span_token.SpanToken):
    """
    Inline role tokens. ("{name}`some code`")
    """

    pattern = re.compile(
        r"(?<!\\|`)(?:\\\\)*{([\:\-\_0-9a-zA-A]*)}(`+)(?!`)(.+?)(?<!`)\2(?!`)",
        re.DOTALL,
    )
    parse_inner = False

    def __init__(self, match):
        self.name = match.group(1)
        content = match.group(3)
        self.children = (
            span_token.RawText(" ".join(re.split("[ \n]+", content.strip()))),
        )


class Math(span_token.SpanToken):

    pattern = re.compile(r"(?<!\\)(?:\\\\)*(\${1,2})([^\$]+?)\1")

    parse_inner = False
    parse_group = 0
    precedence = 2

    @classmethod
    def find(cls, string):
        return _core_matches.value.pop("Math", [])


class Target(span_token.SpanToken):
    """Target tokens. ("(target name)")"""

    pattern = re.compile(r"(?<!\\)(?:\\\\)*\((.+?)\)\=", re.DOTALL)
    parse_inner = False

    def __init__(self, match):
        content = match.group(self.parse_group)
        self.children = (RawText(content),)
        self.target = content


def find_core_tokens(string, root):
    # TODO add speed comparison to original mistletoe implementation
    matches = []
    # escaped denotes that the last cursor position had `\`
    escaped = False
    # delimiter runs are sequences of `*` or `_`
    in_delimiter_run = None
    delimiters = []
    in_image = False
    start = 0
    i = 0

    def _advance_block_regexes(_cursor):
        # TODO Role, etc should probably be added here as well
        return [
            ("InlineCode", InlineCode.pattern.search(string, _cursor)),
            ("Math", Math.pattern.search(string, _cursor)),
        ]

    next_span_blocks = _advance_block_regexes(i)
    while i < len(string):

        # look for there span block (that does not nest any other spans)
        span_block_found = False
        for span_name, span_match in next_span_blocks:
            if span_match is not None and i == span_match.start():
                # restart delimiter runs:
                if in_delimiter_run:
                    delimiters.append(core_tokens.Delimiter(start, i, string))
                in_delimiter_run = None

                _core_matches.value.setdefault(span_name, []).append(span_match)
                i = span_match.end()
                next_span_blocks = _advance_block_regexes(i)
                span_block_found = True
                break
        if span_block_found:
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
                next_span_blocks = _advance_block_regexes(i)
            elif in_image:
                in_image = False
        else:
            escaped = False
        i += 1
    if in_delimiter_run:
        delimiters.append(core_tokens.Delimiter(start, i, string))
    core_tokens.process_emphasis(string, None, delimiters, matches)
    return matches
