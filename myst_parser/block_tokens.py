import re
from typing import Tuple

import attr

from mistletoe import block_tokens
from mistletoe.block_tokens import Heading, ThematicBreak, CodeFence
from mistletoe.attr_doc import autodoc


@autodoc
@attr.s(slots=True, kw_only=True)
class Document(block_tokens.Document):
    """Document token."""

    # TODO this class should eventually be removed

    @classmethod
    def read(cls, *args, **kwargs):
        # default to front matter is True
        kwargs["front_matter"] = kwargs.get("front_matter", True)
        doc = super().read(*args, **kwargs)

        if kwargs.get("propogate_pos", True):
            # TODO this is a placeholder for implementing span level range storage
            # (with start/end character attributes)
            for result in doc.walk():
                if getattr(result.node, "position", None) is None:
                    try:
                        result.node.position = result.parent.position
                    except (AttributeError, TypeError):
                        raise
        return doc


@autodoc
@attr.s(slots=True, kw_only=True)
class LineComment(block_tokens.BlockToken):
    """Line comment start with % """

    content: str = attr.ib(
        repr=False, metadata={"doc": "literal strings rendered as-is"}
    )
    raw: str = attr.ib(repr=False, metadata={"doc": "literal strings rendered as-is"})
    position: Tuple[int, int] = attr.ib(
        metadata={"doc": "Line position in source text (start, end)"}
    )

    pattern = re.compile(r"^ {0,3}\%\s*(.*)")

    @classmethod
    def start(cls, line):
        match_obj = cls.pattern.match(line)
        if match_obj is None:
            return False
        cls.content = (match_obj.group(1) or "").strip()
        return True

    @classmethod
    def read(cls, lines):
        line = next(lines)
        return cls(
            raw=line.splitlines()[0],
            content=cls.content,
            position=(lines.lineno, lines.lineno),
        )


@autodoc
@attr.s(slots=True, kw_only=True)
class BlockBreak(block_tokens.BlockToken):
    """Block break token ``+++``.

    This syntax is myst specific, used to denote the start of a new block of text.
    This constuct's intended use case is for mapping to cell based document formats,
    like jupyter notebooks, to indicate a new text cell.
    """

    content: str = attr.ib(
        repr=False, metadata={"doc": "literal strings rendered as-is"}
    )
    raw: str = attr.ib(repr=False, metadata={"doc": "literal strings rendered as-is"})
    position: Tuple[int, int] = attr.ib(
        metadata={"doc": "Line position in source text (start, end)"}
    )

    pattern = re.compile(r"^ {0,3}(?:(\+)\s*?)(?:\1\s*?){2,}(.*)$")

    def __init__(self, result):
        content, line, lineno = result
        self.content = content
        self.raw = line.splitlines()[0]
        self.range = (lineno, lineno)

    @classmethod
    def start(cls, line):
        match_obj = cls.pattern.match(line)
        if match_obj is None:
            return False
        cls.content = (match_obj.group(2) or "").strip()
        return True

    @classmethod
    def read(cls, lines):
        line = next(lines)
        return cls(
            raw=line.splitlines()[0],
            content=cls.content,
            position=(lines.lineno, lines.lineno),
        )


@autodoc
@attr.s(slots=True, kw_only=True)
class Quote(block_tokens.Quote):
    """Quote token. (`["> # heading\\n", "> paragraph\\n"]`).

    MyST variant, that includes transitions to `LineComment` and `BlockBreak`.
    """

    @classmethod
    def transition(cls, next_line):
        return (
            next_line is None
            or next_line.strip() == ""
            or LineComment.start(next_line)
            or Heading.start(next_line)
            or CodeFence.start(next_line)
            or ThematicBreak.start(next_line)
            or BlockBreak.start(next_line)
            or List.start(next_line)
        )


@autodoc
@attr.s(slots=True, kw_only=True)
class Paragraph(block_tokens.Paragraph):
    """Paragraph token. (`["some\\n", "continuous\\n", "lines\\n"]`)

    Boundary between span-level and block-level tokens.

    MyST variant, that includes transitions to `LineComment` and `BlockBreak`.
    """

    @classmethod
    def transition(cls, next_line):
        return (
            next_line is None
            or next_line.strip() == ""
            or LineComment.start(next_line)
            or Heading.start(next_line)
            or CodeFence.start(next_line)
            or Quote.start(next_line)
            or BlockBreak.start(next_line)
        )


@autodoc
@attr.s(slots=True, kw_only=True)
class List(block_tokens.List):
    """List token (unordered or ordered)

    MyST variant, that includes transitions to `LineComment` and `BlockBreak`.
    """

    @classmethod
    def read(cls, lines):
        start_line = lines.lineno
        leader = None
        next_marker = None
        children = []
        while True:
            item = ListItem.read(lines, next_marker)
            next_marker = item.next_marker
            item_leader = item.leader
            if leader is None:
                leader = item_leader
            elif not cls.same_marker_type(leader, item_leader):
                lines.reset()
                break
            children.append(item)
            if next_marker is None:
                break

        if children:
            # Only consider the last list item loose if there's more than one element
            last_parse_buffer = children[-1]
            last_parse_buffer.loose = (
                len(last_parse_buffer.children) > 1 and last_parse_buffer.loose
            )

        loose = any(item.loose for item in children)
        leader = children[0].leader
        start = None
        if len(leader) != 1:
            start = int(leader[:-1])
        return cls(
            children=children,
            loose=loose,
            start_at=start,
            position=(start_line, lines.lineno),
        )


@autodoc
@attr.s(slots=True, kw_only=True)
class ListItem(block_tokens.ListItem):
    """List items.

    Not included in the parsing process, but called by List.

    MyST variant, that includes transitions to `LineComment` and `BlockBreak`.
    """

    @staticmethod
    def transition(next_line):
        return (
            Heading.start(next_line)
            or LineComment.start(next_line)
            or Quote.start(next_line)
            or CodeFence.start(next_line)
            or ThematicBreak.start(next_line)
            or BlockBreak.start(next_line)
        )
