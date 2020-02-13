import re

from mistletoe import span_token
from mistletoe.span_token import (
    HTMLSpan,
    EscapeSequence,
    AutoLink,
    CoreTokens,
    InlineCode,
    LineBreak,
    RawText,
)
from mistletoe.latex_token import Math

"""
Tokens to be included in the parsing process, in the order specified.
RawText is last as a 'fallback' token
"""
__all__ = (
    "Role",
    "Math",
    "HTMLSpan",
    "EscapeSequence",
    "AutoLink",
    "Target",
    "CoreTokens",
    "InlineCode",
    "LineBreak",
    "RawText",
)
# Note Strikethrough is left out from the core mistletoe tokens,
# since there is no matching element in docutils


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


class Target(span_token.SpanToken):
    """Target tokens. ("!(target name)")"""

    pattern = re.compile(r"(?<!\\)(?:\\\\)*\((.+?)\)\=", re.DOTALL)
    parse_inner = False

    def __init__(self, match):
        content = match.group(self.parse_group)
        self.children = (RawText(content),)
        self.target = content
