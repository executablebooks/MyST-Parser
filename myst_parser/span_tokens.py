import re
from typing import Pattern, Tuple

import attr

from mistletoe import span_tokens
from mistletoe.attr_doc import autodoc

__all__ = ("Role", "Target")


@autodoc
@attr.s(kw_only=True, slots=True)
class Role(span_tokens.SpanToken):
    """
    Inline role tokens. ("{name}`some code`")
    """

    pattern = re.compile(
        r"(?<!\\|`)(?:\\\\)*{([\:\-\_0-9a-zA-A]*)}(`+)(?!`)(.+?)(?<!`)\2(?!`)",
        re.DOTALL,
    )
    parse_inner = False

    role_name: str = attr.ib(metadata={"doc": "The name of the extension point"})
    children = attr.ib(metadata={"doc": "a single RawText node for alternative text."})
    position: Tuple[int, int] = attr.ib(
        default=None,
        repr=False,
        metadata={"doc": "Line position in source text (start, end)"},
    )

    @classmethod
    def read(cls, match: Pattern):
        content = match.group(3)
        return cls(
            role_name=match.group(1),
            children=[
                span_tokens.RawText(" ".join(re.split("[ \n]+", content.strip())))
            ],
        )


@autodoc
@attr.s(kw_only=True, slots=True)
class Target(span_tokens.SpanToken):
    """Target tokens. ("(target name)=")"""

    pattern = re.compile(r"(?<!\\)(?:\\\\)*\((.+?)\)\=", re.DOTALL)
    parse_inner = False

    target: str = attr.ib(metadata={"doc": "link target"})
    children = attr.ib(
        factory=list, metadata={"doc": "a single RawText node for alternative text."}
    )
    position: Tuple[int, int] = attr.ib(
        default=None,
        repr=False,
        metadata={"doc": "Line position in source text (start, end)"},
    )

    @classmethod
    def read(cls, match: Pattern):
        content = match.group(cls.parse_group)
        return cls(target=content, children=[span_tokens.RawText.read(content)])
