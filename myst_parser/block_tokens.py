import re

from mistletoe import block_token, span_token
import mistletoe.block_tokenizer as tokenizer

from mistletoe.block_token import (  # noqa: F401
    tokenize,
    HTMLBlock,
    ThematicBreak,
    Footnote,
    TableRow,
)

"""
Tokens to be included in the parsing process, in the order specified.
"""
__all__ = [
    "HTMLBlock",
    "LineComment",
    "BlockCode",
    "Heading",
    "Quote",
    "CodeFence",
    "ThematicBreak",
    "BlockBreak",
    "List",
    "Table",
    "Footnote",
    "FrontMatter",
    "Paragraph",
]


class FrontMatter(block_token.BlockToken):
    """Front matter YAML block.

    ::

        ---
        a: b
        c: d
        ---

    NOTE: The content of the block should be valid YAML,
    but its parsing (and hence syntax testing) is deferred to the renderers.
    This is so that, given 'bad' YAML,
    the rest of the of document will still be parsed,
    and then the renderers can apply there own error reporting.

    Not included in the parsing process, but called by Document.__init__.
    """

    def __init__(self, lines):
        assert lines and lines[0].startswith("---")
        end_line = None
        for i, line in enumerate(lines[1:]):
            if line.startswith("---"):
                end_line = i + 2
                break
        # TODO raise/report error if closing block not found
        if end_line is None:
            end_line = len(lines)
        self.range = (0, end_line)
        self.content = "\n".join(lines[1 : end_line - 1])
        self.children = []

    @classmethod
    def start(cls, line):
        False

    @classmethod
    def read(cls, lines):
        raise NotImplementedError()

    def __repr__(self):
        return "MyST.{}(range={})".format(self.__class__.__name__, self.range)


class Document(block_token.BlockToken):
    """Document token."""

    def __init__(self, lines, start_line=0, inc_front_matter=True):

        self.footnotes = {}
        block_token._root_node = self
        span_token._root_node = self

        if isinstance(lines, str):
            lines = lines.splitlines(keepends=True)
        lines = [line if line.endswith("\n") else "{}\n".format(line) for line in lines]
        self.children = []
        if lines and lines[0].startswith("---"):
            front_matter = FrontMatter(lines)
            if inc_front_matter:
                self.children.append(front_matter)
            start_line = front_matter.range[1]
            lines = lines[start_line:]
        self.children.extend(tokenize(lines, start_line))

        span_token._root_node = None
        block_token._root_node = None

    def __repr__(self):
        return "MyST.{}(blocks={})".format(self.__class__.__name__, len(self.children))


class LineComment(block_token.BlockToken):
    """Line comment start with % """

    pattern = re.compile(r"^ {0,3}\%\s*(.*)")

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
        cls.content = (match_obj.group(1) or "").strip()
        return True

    @classmethod
    def read(cls, lines):
        line = next(lines)
        return cls.content, line, lines.lineno

    def __repr__(self):
        return "MyST.{}(range={})".format(self.__class__.__name__, self.range)


class BlockBreak(block_token.BlockToken):
    """Block break token ``+++``.

    This syntax is myst specific, used to denote the start of a new block of text.
    This constuct's intended use case is for mapping to cell based document formats,
    like jupyter notebooks, to indicate a new text cell.
    """

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
        return cls.content, line, lines.lineno

    def __repr__(self):
        return "MyST.{}(range={})".format(self.__class__.__name__, self.range)


class Heading(block_token.Heading):
    """
    Heading token. (["### some heading ###\\n"])
    Boundary between span-level and block-level tokens.

    Attributes:
        level (int): heading level.
        children (list): inner tokens.
    """

    def __init__(self, match):
        self.level, content, self.range = match
        super(block_token.Heading, self).__init__(content, span_token.tokenize_inner)

    @classmethod
    def read(cls, lines):
        next(lines)
        return cls.level, cls.content, (lines.lineno, lines.lineno)

    def __repr__(self):
        return "MyST.{}(range={},level={})".format(
            self.__class__.__name__, self.range, self.level
        )


class SetextHeading(block_token.SetextHeading):
    """
    Setext headings.

    Not included in the parsing process, but called by Paragraph.__new__.
    """

    def __init__(self, result):
        lines, self.range = result
        self.level = 1 if lines.pop().lstrip().startswith("=") else 2
        content = "\n".join([line.strip() for line in lines])
        super(block_token.SetextHeading, self).__init__(
            content, span_token.tokenize_inner
        )

    def __repr__(self):
        return "MyST.{}(range={},level={})".format(
            self.__class__.__name__, self.range, self.level
        )


class Quote(block_token.Quote):
    """
    Quote token. (["> # heading\\n", "> paragraph\\n"])
    """

    def __init__(self, result):
        parse_buffer, self.range = result
        # span-level tokenizing happens here.
        self.children = tokenizer.make_tokens(parse_buffer)

    @classmethod
    def read(cls, lines):
        # first line
        start_line = lines.lineno + 1
        line = cls.convert_leading_tabs(next(lines).lstrip()).split(">", 1)[1]
        if len(line) > 0 and line[0] == " ":
            line = line[1:]
        line_buffer = [line]

        # set booleans
        in_code_fence = CodeFence.start(line)
        in_block_code = BlockCode.start(line)
        blank_line = line.strip() == ""

        # loop
        next_line = lines.peek()
        while (
            next_line is not None
            and next_line.strip() != ""
            # TODO transition checks should only be made on 'active' tokens
            and not LineComment.start(next_line)
            and not Heading.start(next_line)
            and not CodeFence.start(next_line)
            and not ThematicBreak.start(next_line)
            and not BlockBreak.start(next_line)
            and not List.start(next_line)
        ):
            stripped = cls.convert_leading_tabs(next_line.lstrip())
            prepend = 0
            if stripped[0] == ">":
                # has leader, not lazy continuation
                prepend += 1
                if stripped[1] == " ":
                    prepend += 1
                stripped = stripped[prepend:]
                in_code_fence = CodeFence.start(stripped)
                in_block_code = BlockCode.start(stripped)
                blank_line = stripped.strip() == ""
                line_buffer.append(stripped)
            elif in_code_fence or in_block_code or blank_line:
                # not paragraph continuation text
                break
            else:
                # lazy continuation, preserve whitespace
                line_buffer.append(next_line)
            next(lines)
            next_line = lines.peek()

        # block level tokens are parsed here, so that footnotes
        # in quotes can be recognized before span-level tokenizing.
        Paragraph.parse_setext = False
        # TODO headers in quotes??
        parse_buffer = tokenizer.tokenize_block(
            line_buffer, block_token._token_types.value, start_line
        )
        Paragraph.parse_setext = True
        return parse_buffer, (start_line, lines.lineno)

    def __repr__(self):
        return "MyST.{}(range={},children={})".format(
            self.__class__.__name__, self.range, len(self.children)
        )


class Paragraph(block_token.Paragraph):
    """
    Paragraph token. (["some\\n", "continuous\\n", "lines\\n"])
    Boundary between span-level and block-level tokens.
    """

    def __new__(cls, result):
        if isinstance(result, SetextHeading):
            # setext heading token, return directly
            return result
        return block_token.BlockToken.__new__(cls)

    def __init__(self, result):
        lines, line_range = result
        self.range = line_range
        content = "".join([line.lstrip() for line in lines]).strip()
        block_token.BlockToken.__init__(self, content, span_token.tokenize_inner)

    @classmethod
    def read(cls, lines):
        line_buffer = [next(lines)]
        start_line = lines.lineno
        next_line = lines.peek()
        while (
            next_line is not None
            and next_line.strip() != ""
            and not LineComment.start(next_line)
            and not Heading.start(next_line)
            and not CodeFence.start(next_line)
            and not Quote.start(next_line)
        ):

            # check if next_line starts List
            list_pair = ListItem.parse_marker(next_line)
            if len(next_line) - len(next_line.lstrip()) < 4 and list_pair is not None:
                prepend, leader = list_pair
                # non-empty list item
                if next_line[:prepend].endswith(" "):
                    # unordered list, or ordered list starting from 1
                    if not leader[:-1].isdigit() or leader[:-1] == "1":
                        break

            # check if next_line starts HTMLBlock other than type 7
            # TODO ignore HTMLBlock?
            html_block = block_token.HTMLBlock.start(next_line)
            if html_block and html_block != 7:
                break

            # check if we see a setext underline
            if cls.parse_setext and cls.is_setext_heading(next_line):
                line_buffer.append(next(lines))
                return SetextHeading((line_buffer, (start_line, lines.lineno)))

            # check if we have a ThematicBreak / BlockBreak (has to be after setext)
            if ThematicBreak.start(next_line) or BlockBreak.start(next_line):
                break

            # no other tokens, we're good
            line_buffer.append(next(lines))
            next_line = lines.peek()
        return line_buffer, (start_line, lines.lineno)

    def __repr__(self):
        return "MyST.{}(range={},children={})".format(
            self.__class__.__name__, self.range, len(self.children)
        )


class BlockCode(block_token.BlockCode):
    """
    Indented code.

    Attributes:
        children (list): contains a single span_token.RawText token.
        language (str): always the empty string.
    """

    def __init__(self, result):
        lines, self.range = result
        self.language = ""
        self.children = (span_token.RawText("".join(lines).strip("\n") + "\n"),)

    @classmethod
    def read(cls, lines):
        start_line = lines.lineno
        line_buffer = []
        for line in lines:
            if line.strip() == "":
                line_buffer.append(line.lstrip(" ") if len(line) < 5 else line[4:])
                continue
            if not line.replace("\t", "    ", 1).startswith("    "):
                lines.backstep()
                break
            line_buffer.append(cls.strip(line))
        return line_buffer, (start_line, lines.lineno)

    def __repr__(self):
        return "MyST.{}(range={},language={})".format(
            self.__class__.__name__, self.range, self.language
        )


class CodeFence(block_token.CodeFence):
    """
    Code fence. (["```sh\\n", "rm -rf /", ..., "```"])
    Boundary between span-level and block-level tokens.

    Attributes:
        children (list): contains a single span_token.RawText token.
        language (str): language of code block (default to empty).
    """

    pattern = re.compile(r"^( {0,3})((?:`|~){3,}) *([^`~\s]*) *([^`~]*)$")

    def __init__(self, match):
        lines, open_info, self.range = match
        self.language = span_token.EscapeSequence.strip(open_info[2])
        self.arguments = span_token.EscapeSequence.strip(open_info[3].splitlines()[0])
        self.children = (span_token.RawText("".join(lines)),)

    @classmethod
    def start(cls, line):
        match_obj = cls.pattern.match(line)
        if not match_obj:
            return False
        prepend, leader, lang, arguments = match_obj.groups()
        if leader[0] in lang or leader[0] in line[match_obj.end() :]:
            return False
        cls._open_info = len(prepend), leader, lang, arguments
        return True

    @classmethod
    def read(cls, lines):
        start_line = lines.lineno
        next(lines)
        line_buffer = []
        for line in lines:
            stripped_line = line.lstrip(" ")
            diff = len(line) - len(stripped_line)
            if (
                stripped_line.startswith(cls._open_info[1])
                and len(stripped_line.split(maxsplit=1)) == 1
                and diff < 4
            ):
                break
            if diff > cls._open_info[0]:
                stripped_line = " " * (diff - cls._open_info[0]) + stripped_line
            line_buffer.append(stripped_line)
        return line_buffer, cls._open_info, (start_line, lines.lineno)

    def __repr__(self):
        return "MyST.{}(range={},language={})".format(
            self.__class__.__name__, self.range, self.language
        )


class Table(block_token.Table):
    """
    Table token.

    Attributes:
        has_header (bool): whether table has header row.
        column_align (list): align options for each column (default to [None]).
        children (list): inner tokens (TableRows).
    """

    def __init__(self, result):
        lines, self.range = result
        if "---" in lines[1]:
            self.column_align = [
                self.parse_align(column) for column in self.split_delimiter(lines[1])
            ]
            self.header = TableRow(lines[0], self.column_align)
            self.children = [TableRow(line, self.column_align) for line in lines[2:]]
        else:
            self.column_align = [None]
            self.children = [TableRow(line) for line in lines]

    @staticmethod
    def read(lines):
        start_line = lines.lineno + 1
        lines.anchor()
        line_buffer = [next(lines)]
        while lines.peek() is not None and "|" in lines.peek():
            line_buffer.append(next(lines))
        if len(line_buffer) < 2 or "---" not in line_buffer[1]:
            lines.reset()
            return None
        return line_buffer, (start_line, lines.lineno)

    def __repr__(self):
        return "MyST.{}(range={},rows={})".format(
            self.__class__.__name__, self.range, len(self.children)
        )


class List(block_token.List):
    def __init__(self, matches):
        self.children = [ListItem(*match) for match in matches]
        self.loose = any(item.loose for item in self.children)
        leader = self.children[0].leader
        self.start = None
        if len(leader) != 1:
            self.start = int(leader[:-1])

    def __repr__(self):
        return "MyST.{}(items={})".format(self.__class__.__name__, len(self.children))


class ListItem(block_token.ListItem):
    @staticmethod
    def other_token(line):
        return (
            Heading.start(line)
            or LineComment.start(line)
            or Quote.start(line)
            or CodeFence.start(line)
            or ThematicBreak.start(line)
            or BlockBreak.start(line)
        )

    def __repr__(self):
        return "MyST.{}(children={})".format(
            self.__class__.__name__, len(self.children)
        )
