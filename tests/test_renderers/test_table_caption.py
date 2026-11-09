"""Test ``{table}`` captions that wrap onto the lines after the opening line (#1104).

MyST takes a directive's argument from its opening line only,
so the rest of a hard-wrapped caption is parsed as a paragraph before the table,
which docutils' ``table`` directive rejects with "exactly one table expected".
The body is parsed as before, and only that failing shape is changed:
a paragraph that directly follows the opening line (or the options block),
then a table, becomes the end of the table's caption.
"""

from io import StringIO

import pytest
from docutils import nodes
from docutils.core import publish_doctree, publish_string
from docutils.parsers.rst import directives
from docutils.parsers.rst.directives.tables import RSTTable

from myst_parser.docutils_ import Parser
from myst_parser.mocking import MockState, MockTableState

TABLE = "| a | b |\n|---|---|\n| 1 | 2 |"
WRAPPED = "Mid-syllable marks that must be tagged for sorting with"
WRAPPED_CAPTION = f"{WRAPPED} above-base consonants"
EXTENSIONS = [
    "alert",
    "amsmath",
    "attrs_block",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "gfm_autolink",
    "html_admonition",
    "html_image",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]
"""Every syntax extension that needs no extra dependency."""


def _source(first_line: str, body: str, fence: str = "~~~") -> str:
    opening = f"{fence}{{table}} {first_line}" if first_line else f"{fence}{{table}}"
    return f"{opening}\n{body}\n{fence}\n"


def _settings(extensions: list[str], stream: StringIO) -> dict:
    return {
        "myst_enable_extensions": extensions,
        "myst_substitutions": {"sub": "S"},
        "warning_stream": stream,
    }


def _render(text: str, extensions: list[str]) -> tuple[nodes.document, str]:
    stream = StringIO()
    doctree = publish_doctree(
        text, parser=Parser(), settings_overrides=_settings(extensions, stream)
    )
    return doctree, stream.getvalue()


def _pseudoxml(text: str, extensions: list[str]) -> str:
    stream = StringIO()
    settings = {**_settings(extensions, stream), "output_encoding": "unicode"}
    output = publish_string(
        text, parser=Parser(), writer_name="pseudoxml", settings_overrides=settings
    )
    return f"{output}\n{stream.getvalue()}"


@pytest.mark.parametrize(
    "first_line,body,caption",
    [
        pytest.param(
            WRAPPED, "above-base consonants\n\n" + TABLE, WRAPPED_CAPTION, id="wrapped"
        ),
        pytest.param(
            WRAPPED,
            "   above-base consonants\n\n" + TABLE,
            WRAPPED_CAPTION,
            id="wrapped-indented",
        ),
        pytest.param("Cap", "continued\n" + TABLE, "Cap continued", id="no-blank"),
        pytest.param(
            "Cap",
            "continued\nand more\n\n\n" + TABLE,
            "Cap continued\nand more",
            id="several-lines-then-blanks",
        ),
        pytest.param(
            "Cap",
            "continued\n\na | b\n--|--\n1 | 2",
            "Cap continued",
            id="pipeless-table",
        ),
        pytest.param(
            "Cap",
            "continued\na | b\n--|--\n1 | 2",
            "Cap continued",
            id="pipeless-table-no-blank",
        ),
        pytest.param(
            "Cap",
            "continued\n\n| a | b |\n| :-- | --: |\n| 1 | 2 |",
            "Cap continued",
            id="aligned-table",
        ),
        pytest.param(
            "",
            "Long caption\nwrapped\n\n" + TABLE,
            "Long caption\nwrapped",
            id="no-argument",
        ),
        pytest.param(
            "Cap",
            "continued with *emphasis* and `code`\n" + TABLE,
            "Cap continued with emphasis and code",
            id="inline-markup",
        ),
    ],
)
@pytest.mark.parametrize("extensions", [[], EXTENSIONS], ids=["none", "all"])
def test_wrapped_caption(first_line, body, caption, extensions):
    """The paragraph directly after the opening line ends the table's caption."""
    doctree, warnings = _render(_source(first_line, body), extensions)
    assert not warnings
    assert len(doctree) == 1
    table = doctree[0]
    assert isinstance(table, nodes.table)
    assert isinstance(table[0], nodes.title)
    assert table[0].astext() == caption
    assert table[0].line == 1


def test_wrapped_caption_keeps_inline_nodes():
    """The continuation keeps its inline markup, as parsed in the paragraph."""
    doctree, _ = _render(_source("Cap *a*", "*b* end\n" + TABLE), [])
    title = doctree[0][0]
    assert [type(child) for child in title.children] == [
        nodes.Text,
        nodes.emphasis,
        nodes.Text,
        nodes.emphasis,
        nodes.Text,
    ]
    assert title.astext() == "Cap a b end"


@pytest.mark.parametrize(
    "fence,extensions",
    [("```", []), ("~~~", []), (":::", ["colon_fence"])],
)
@pytest.mark.parametrize(
    "body,ids",
    [
        pytest.param(":name: tbl\ncontinued\n\n" + TABLE, ["tbl"], id="options"),
        pytest.param("---\nname: tbl\n---\ncontinued\n" + TABLE, ["tbl"], id="yaml"),
    ],
)
def test_wrapped_caption_after_options(fence, extensions, body, ids):
    """The caption may continue after the options block, and the options apply."""
    doctree, warnings = _render(_source("Cap", body, fence), extensions)
    assert not warnings
    table = doctree[0]
    assert table["ids"] == ids
    assert table[0].astext() == "Cap continued"


def test_wrapped_caption_source_lines():
    """The table body is parsed as before, so its source lines are unchanged."""
    doctree, warnings = _render(
        _source("Cap", "continued\nmore\n| a | b |\n|---|---|\n| 1 | {nope}`x` |"), []
    )
    assert doctree[0][0].astext() == "Cap continued\nmore"
    message = 'Unknown interpreted text role "nope". [myst.role_unknown]'
    assert warnings.splitlines() == [f"<string>:6: (WARNING/2) {message}"]


class _ListAllTable(RSTTable):
    """A table directive with its own ``run``, which outputs the whole body."""

    def run(self) -> list[nodes.Node]:
        node = nodes.Element()
        self.state.nested_parse(self.content, self.content_offset, node)
        return node.children[:]


def test_table_subclass_with_own_run_unchanged(monkeypatch):
    """Only docutils' own ``run`` (which rejects this body) gets the caption joining,
    since a directive that overrides it may accept a paragraph before the table.
    """
    monkeypatch.setitem(directives._directives, "list-all-table", _ListAllTable)
    doctree, warnings = _render(
        "```{list-all-table} Cap\ncontinued\n" + TABLE + "\n```\n", []
    )
    assert not warnings
    assert [type(child) for child in doctree.children] == [nodes.paragraph, nodes.table]
    assert doctree[0].astext() == "continued"


@pytest.mark.parametrize(
    "first_line,body,extensions,caption",
    [
        # valid tables: a link or footnote definition, a directive or a line of
        # block attributes before the table render nothing
        ("Cap", "[x]: https://example.com\n\n" + TABLE, [], "Cap"),
        ("Cap", "[a\\]b]: https://example.com\n" + TABLE, [], "Cap"),
        ("Cap", "[foo\nbar]: https://example.com\n\n" + TABLE, [], "Cap"),
        ("", "[Smith \\[2020\\]]: https://example.com\n\n" + TABLE, [], None),
        ("Cap", "```{default-role} math\n```\n" + TABLE, [], "Cap"),
        ("Cap", "{.striped}\n" + TABLE, ["attrs_block"], "Cap"),
        ("Cap", '{#mytbl .striped key="v"}\n' + TABLE, ["attrs_block"], "Cap"),
        ("", "{.striped}\n" + TABLE, ["attrs_block"], None),
        ("Cap", ":name: x\n{.striped}\n" + TABLE, ["attrs_block"], "Cap"),
        ("Cap", "\n" + TABLE, [], "Cap"),
        # errors: a paragraph separated from the opening line by a blank line
        ("Cap", "\nSome prose.\n\n" + TABLE, [], "error"),
        ("", "\nSome prose.\n\n" + TABLE, [], "error"),
        ("Cap", ":name: tbl\n\nSome prose.\n\n" + TABLE, [], "error"),
        # errors: option lines after a caption line would be lost in the caption
        ("Cap", "continued\n:name: tbl\n\n" + TABLE, [], "error"),
        ("Cap", "continued\n:name: tbl\n" + TABLE, [], "error"),
        ("Cap", ":name: a\ncontinued\n:align: center\n\n" + TABLE, [], "error"),
        ("Cap", "continued\n---\nname: tbl\n---\n\n" + TABLE, [], "error"),
        # errors: other blocks before the table, or not just a table after it
        ("Cap", "[^1]: note\n" + TABLE, [], "error"),
        ("Cap", "(label)=\n\n" + TABLE, [], "error"),
        ("Cap", "% comment\n" + TABLE, [], "error"),
        ("Cap", "<!-- comment -->\n" + TABLE, [], "error"),
        ("Cap", "+++\n\n" + TABLE, [], "error"),
        ("Cap", "- item\n" + TABLE, [], "error"),
        ("Cap", "$$\nx\n$$\n" + TABLE, ["dollarmath"], "error"),
        ("Cap", "{{ sub }}\n" + TABLE, ["substitution"], "error"),
        ("Cap", "{.striped}\ncontinued\n" + TABLE, ["attrs_block"], "error"),
        ("Cap", "[x]: https://example.com\ncontinued\n" + TABLE, [], "error"),
        ("Cap", "continued\n\nmore\n\n" + TABLE, [], "error"),
        ("Cap", "continued\n" + TABLE + "\n\nafter", [], "error"),
        ("Cap", "continued\n\nnot a table", [], "error"),
        ("Cap", "continued\n\n| a | b |\n| 1 | 2 |", [], "error"),
    ],
)
def test_not_a_wrapped_caption(monkeypatch, first_line, body, extensions, caption):
    """Any other body renders exactly as it would without the caption joining:
    a valid table keeps its caption (``None`` for no caption),
    and anything else still fails with "exactly one table expected".
    """
    text = _source(first_line, body)
    doctree, warnings = _render(text, extensions)
    if caption == "error":
        assert "exactly one table expected" in warnings
        assert not list(doctree.findall(nodes.table))
    else:
        assert not warnings
        (table,) = doctree.findall(nodes.table)
        title = table[0].astext() if isinstance(table[0], nodes.title) else None
        assert title == caption
    output = _pseudoxml(text, extensions)
    monkeypatch.setattr(MockTableState, "nested_parse", MockState.nested_parse)
    assert output == _pseudoxml(text, extensions)


@pytest.mark.parametrize(
    "first_line,continuation",
    [("Outer", "caption"), ("", "Outer caption")],
    ids=["argument", "no-argument"],
)
def test_wrapped_caption_on_titled_table(first_line, continuation):
    """A table that already has a title (here from ``list-table``) renders
    as with the whole caption on the opening line:
    the continuation joins the opening line's caption, never the inner title.
    """
    inner = "```{list-table} Inner\n* - a\n  - b\n```"
    wrapped = _pseudoxml(_source(first_line, f"{continuation}\n{inner}"), [])
    assert wrapped == _pseudoxml(_source("Outer caption", inner), [])
    assert "Outer caption" in wrapped


def test_wrapped_caption_with_system_message():
    """System messages beside the paragraph and the table do not stop the joining,
    and are output after the table.
    """
    doctree, warnings = _render(
        _source("Cap", "continued\n```{unknown}\n```\n" + TABLE), []
    )
    assert "Unknown directive type: 'unknown'" in warnings
    assert "exactly one table expected" not in warnings
    table, *messages = doctree.children
    assert isinstance(table, nodes.table)
    assert table[0].astext() == "Cap continued"
    assert messages
    assert all(isinstance(message, nodes.system_message) for message in messages)
