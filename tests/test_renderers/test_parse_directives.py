import json
import time
from pathlib import Path

import pytest
import yaml
from docutils.parsers.rst.directives.admonitions import Admonition, Note
from docutils.parsers.rst.directives.body import Rubric
from docutils.parsers.rst.directives.misc import TestDirective as DocutilsTestDirective
from docutils.parsers.rst.directives.tables import RSTTable
from markdown_it import MarkdownIt
from sphinx.directives.code import CodeBlock

from myst_parser.parsers.directives import MarkupError, parse_directive_text
from myst_parser.parsers.options import (
    TokenizeError,
    options_to_items,
    options_to_tokens,
)

FIXTURE_PATH = Path(__file__).parent.joinpath("fixtures")


@pytest.mark.param_file(FIXTURE_PATH / "option_parsing.yaml", "yaml")
def test_option_parsing(file_params):
    """Test parsing of directive options."""
    result, state = options_to_items(file_params.content)
    file_params.assert_expected(
        json.dumps(
            {"dict": result, "comments": state.has_comments},
            ensure_ascii=False,
            indent=2,
        ),
        rstrip_lines=True,
    )


@pytest.mark.param_file(FIXTURE_PATH / "option_parsing_errors.yaml", "yaml")
def test_option_parsing_errors(file_params):
    """Test parsing of directive options."""
    try:
        options_to_items(file_params.content)
    except TokenizeError as err:
        result = str(err)
    else:
        result = "No error"
    file_params.assert_expected(result, rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "directive_parsing.txt")
def test_parsing(file_params):
    """Test parsing of directive text."""
    tokens = MarkdownIt("commonmark").parse(file_params.content)
    assert len(tokens) == 1 and tokens[0].type == "fence"
    name, *first_line = tokens[0].info.split(maxsplit=1)
    if name == "{note}":
        klass = Note
    elif name == "{admonition}":
        klass = Admonition
    elif name == "{code-block}":
        klass = CodeBlock
    else:
        raise AssertionError(f"Unknown directive: {name}")
    try:
        result = parse_directive_text(
            klass, first_line[0] if first_line else "", tokens[0].content, line=0
        )
    except MarkupError as err:
        outcome = f"error: {err}"
    else:
        outcome = yaml.safe_dump(
            {
                "arguments": result.arguments,
                "options": result.options,
                "body": result.body,
                "content_offset": result.body_offset,
                "warnings": [repr(w) for w in result.warnings],
            },
            sort_keys=True,
        )
    file_params.assert_expected(outcome, rstrip_lines=True)


@pytest.mark.parametrize(
    "descript,klass,arguments,content", [("no content", Rubric, "", "a")]
)
def test_parsing_errors(descript, klass, arguments, content):
    with pytest.raises(MarkupError):
        parse_directive_text(klass, arguments, content)


def test_parsing_full_yaml():
    result = parse_directive_text(
        Note, "", "---\na: [1]\n---\ncontent", validate_options=False
    )
    assert not result.warnings
    assert result.options == {"a": [1]}
    assert result.body == ["content"]


def test_additional_options():
    """Allow additional options to be passed to a directive."""
    # this should be fine
    result = parse_directive_text(
        Note, "", "content", additional_options={"class": "bar"}
    )
    assert not result.warnings
    assert result.options == {"class": ["bar"]}
    assert result.body == ["content"]
    # body on first line should also be fine
    result = parse_directive_text(
        Note, "content", "other", additional_options={"class": "bar"}
    )
    assert not result.warnings
    assert result.options == {"class": ["bar"]}
    assert result.body == ["content", "other"]
    # additional option should not take precedence
    result = parse_directive_text(
        Note, "content", ":class: foo", additional_options={"class": "bar"}
    )
    assert not result.warnings
    assert result.options == {"class": ["foo"]}
    assert result.body == ["content"]
    # this should warn about the unknown option
    result = parse_directive_text(
        Note, "", "content", additional_options={"foo": "bar"}
    )
    assert len(result.warnings) == 1
    assert "Unknown option" in result.warnings[0].msg


def test_colon_options_stop_at_colon_fence():
    """Options parsing should stop when encountering a colon fence (3+ colons)."""
    result = parse_directive_text(Note, "", ":class: xxx\n::::{other}\ncontent\n::::")
    assert result.options == {"class": ["xxx"]}
    assert result.body == ["::::{other}", "content", "::::"]


def test_option_warning_lines_yaml_block():
    """Option warnings carry per-key source lines for a ``---`` YAML block."""
    result = parse_directive_text(
        Note, "", "---\nclass: [1]\nname: ok\nfoo: bar\n---\nbody", line=3
    )
    assert len(result.warnings) == 2
    # line 3 fence, 4 `---`, 5 `class: [1]`
    assert result.warnings[0].msg.startswith("Invalid option value for 'class'")
    assert result.warnings[0].lineno == 5
    assert result.warnings[1].msg == (
        "Unknown option key: 'foo' (allowed: ['class', 'name'])"
    )
    assert result.warnings[1].lineno == 7
    assert result.body == ["body"]
    assert result.body_offset == 5


def test_option_warning_lines_colon_block():
    """Option warnings carry per-key source lines for a ``:opt:`` block."""
    result = parse_directive_text(Note, "", ":class: [1]\n:foo: bar\n\nbody", line=3)
    assert len(result.warnings) == 2
    assert result.warnings[0].msg.startswith("Invalid option value for 'class'")
    assert result.warnings[0].lineno == 4
    assert result.warnings[1].msg == (
        "Unknown option key: 'foo' (allowed: ['class', 'name'])"
    )
    assert result.warnings[1].lineno == 5
    assert result.body == ["body"]
    assert result.body_offset == 3


@pytest.mark.parametrize(
    ("first_line", "content", "offset"),
    [
        # colon-style option block
        pytest.param("", ":class: tip\nbody", 1, id="colon"),
        pytest.param("", ":class: tip\nbody\n\n\n", 1, id="colon-blanks"),
        # a fence body always ends in "\n", so one blank line before the
        # closing fence is enough to trigger #1177
        pytest.param("", ":class: tip\nbody\n\n", 1, id="colon-one-blank"),
        # blank separator line between the options and the body
        pytest.param("", ":class: tip\n\nbody\n\n", 2, id="colon-separator"),
        # yaml-style option block
        pytest.param("", "---\nclass: tip\n---\nbody", 3, id="yaml"),
        pytest.param("", "---\nclass: tip\n---\nbody\n\n\n", 3, id="yaml-blanks"),
        # text trailing the closing `---` is the first body line,
        # sitting on the closing line itself (#1164)
        pytest.param(
            "", "---\nclass: tip\n--- body\nmore\n\n", 2, id="yaml-closer-text"
        ),
        # unclosed `---` block: everything is options, there is no body
        pytest.param("", "---\nclass: tip\n\n", 3, id="yaml-unclosed"),
        # no option block: unaffected
        pytest.param("", "body\n\n", 0, id="no-options"),
        # body text on the first line sits on the opening line itself: -1 (#1164)
        pytest.param("first", "second\n\n", -1, id="first-line"),
        # ... and with an option block, the offset is right for the body lines
        # after the merged first line (``body`` is two lines below the opener)
        pytest.param("first", ":class: tip\nbody\n\n", 0, id="first-line-colon"),
    ],
)
def test_body_offset_not_inflated_by_trailing_blank_lines(first_line, content, offset):
    """A body ending in blank lines must not inflate ``body_offset`` (#1177)."""
    result = parse_directive_text(Note, first_line, content)
    assert result.body_offset == offset


@pytest.mark.parametrize(
    ("directive", "validate_options", "content", "offset"),
    [
        # options read as plain YAML, without validation (as myst-nb does)
        pytest.param(Note, False, ":class: tip\nbody\n\n", 1, id="as-yaml-colon"),
        pytest.param(
            Note, False, "---\nclass: tip\n---\nbody\n\n", 3, id="as-yaml-yaml"
        ),
        # docutils' test directive accepts any option, on its own return path
        pytest.param(
            DocutilsTestDirective, True, ":option: x\nbody\n\n", 1, id="test-directive"
        ),
    ],
)
def test_body_offset_trailing_blank_other_option_paths(
    directive, validate_options, content, offset
):
    """The #1177 fix also holds where options are not validated against a spec."""
    result = parse_directive_text(
        directive, "", content, validate_options=validate_options
    )
    assert result.body == ["body"]
    assert result.body_offset == offset


def test_option_warning_lines_none():
    """Without a known directive line, option warnings have no line number."""
    result = parse_directive_text(
        Note, "", "---\nclass: [1]\nname: ok\nfoo: bar\n---\nbody"
    )
    assert len(result.warnings) == 2
    assert all(w.lineno is None for w in result.warnings)


def test_option_tokenize_error_line():
    """A tokenize error carries the source line of the problem mark."""
    result = parse_directive_text(Note, "", '---\nclass: "unclosed\n---\nbody', line=1)
    assert len(result.warnings) == 1
    # fence 1, `---` 2, bad line 3
    assert result.warnings[0].msg.startswith("Invalid options format")
    assert result.warnings[0].lineno == 3
    assert result.body == ["body"]


def test_yaml_block_closing_delimiter_trailing_text():
    """Text trailing a ``---`` closing delimiter becomes the first body line.

    As previously, any line starting with three dashes closes the block, but
    the split is now line-based, so the trailing text keeps an exact source
    line mapping (it was previously merged into the following line's mapping).
    """
    result = parse_directive_text(
        Note, "", "---\nclass: tip\n--- foo\n---\nbody", line=1
    )
    assert not result.warnings
    assert result.options == {"class": ["tip"]}
    # "foo" is kept as its own body line, mapping to source line
    # 1 (fence) + 2 (body_offset) + 1 = 4, the `--- foo` line itself
    assert result.body == ["foo", "---", "body"]
    assert result.body_offset == 2
    # a dashes-only closer with trailing whitespace closes without a leak
    result2 = parse_directive_text(Note, "", "---\nclass: tip\n---   \nbody", line=1)
    assert not result2.warnings
    assert result2.options == {"class": ["tip"]}
    assert result2.body == ["body"]


def test_option_comment_warning_line():
    """The comments warning points at the (first) comment's own line."""
    result = parse_directive_text(
        Note, "", "---\nclass: tip\n# a comment\n---\nbody", line=1
    )
    assert len(result.warnings) == 1
    assert "# comments" in result.warnings[0].msg
    assert result.warnings[0].lineno == 4


def test_as_yaml_error_line():
    """The full-YAML (``validate_options=False``) parse errors carry lines."""
    result = parse_directive_text(
        Note, "", "---\na: {\n---\nbody", line=1, validate_options=False
    )
    assert len(result.warnings) == 1
    assert result.warnings[0].msg == "Invalid options format (bad YAML)"
    assert result.warnings[0].lineno == 3
    assert result.body == ["body"]


def test_options_to_tokens():
    """``options_to_tokens`` yields key/value token pairs with source lines."""
    text = "a: 1\nb: |\n  multi\n  line\nc:\n"
    tokens, _state = options_to_tokens(text)
    assert [key.value for key, _ in tokens] == ["a", "b", "c"]
    assert [key.start.line for key, _ in tokens] == [0, 1, 4]
    values = [value.value if value is not None else None for _, value in tokens]
    assert values == ["1", "multi\nline\n", None]
    items, _ = options_to_items(text)
    assert items == [
        (key.value, value.value if value is not None else "") for key, value in tokens
    ]


def test_options_to_tokens_comment_lines():
    """``State.comment_lines`` records each comment's line, exactly once."""
    _, state = options_to_tokens("# first\na: 1 # second\n# third\nb: 2\n")
    assert state.has_comments
    assert state.comment_lines == [0, 1, 2]


TABLE_BODY = "| a | b |\n|---|---|\n| 1 | 2 |"
WRAPPED = "Mid-syllable marks that must be tagged for sorting with"
WRAPPED_CAPTION = f"{WRAPPED} above-base consonants"


@pytest.mark.parametrize(
    "first_line,content,caption,body_offset",
    [
        pytest.param(
            WRAPPED,
            "above-base consonants\n\n" + TABLE_BODY,
            WRAPPED_CAPTION,
            2,
            id="wrapped",
        ),
        pytest.param(
            WRAPPED,
            "   above-base consonants\n\n" + TABLE_BODY,
            WRAPPED_CAPTION,
            2,
            id="wrapped-indented",
        ),
        pytest.param(
            "Cap",
            "continued\nand more\n\n\n" + TABLE_BODY,
            "Cap continued and more",
            4,
            id="several-lines-then-blanks",
        ),
        pytest.param(
            "Cap", "continued\n" + TABLE_BODY, "Cap continued", 1, id="no-blank"
        ),
        pytest.param(
            "Cap",
            "continued\n\na | b\n--|--\n1 | 2",
            "Cap continued",
            2,
            id="pipeless-table",
        ),
        pytest.param(
            "Cap",
            "continued\n\n| a | b |\n| :-- | --: |\n| 1 | 2 |",
            "Cap continued",
            2,
            id="aligned-table",
        ),
        pytest.param(
            "Cap",
            ":name: tbl\ncontinued\n\n" + TABLE_BODY,
            "Cap continued",
            3,
            id="after-options",
        ),
        pytest.param(
            "Cap",
            "---\nname: tbl\n---\ncontinued\n\n" + TABLE_BODY,
            "Cap continued",
            5,
            id="after-yaml-options",
        ),
        pytest.param(
            "",
            "Long caption\nwrapped\n\n" + TABLE_BODY,
            "Long caption wrapped",
            3,
            id="no-first-line-argument",
        ),
    ],
)
def test_table_wrapped_caption_folded_into_argument(
    first_line, content, caption, body_offset
):
    """A ``{table}`` caption may wrap onto the lines directly after the opening line.

    MyST takes directive arguments from the opening line only, so without the fold
    a hard-wrapped caption becomes a leading paragraph in the body,
    and the table directive fails with "exactly one table expected" (#1104).
    ``body_offset`` must still point at the table's first line,
    so that warnings inside the table report the right source line.
    """
    result = parse_directive_text(RSTTable, first_line, content, line=1)
    assert result.arguments == [caption]
    assert result.body_offset == body_offset
    assert result.body == content.splitlines()[body_offset:]
    assert "|" in result.body[0]
    assert not result.warnings


@pytest.mark.parametrize(
    "first_line,content,body_offset",
    [
        pytest.param(
            "Cap", "\nSome prose.\n\n" + TABLE_BODY, 1, id="blank-after-opening"
        ),
        pytest.param("", "\nSome prose.\n\n" + TABLE_BODY, 1, id="blank-no-argument"),
        pytest.param(
            "Cap",
            ":name: tbl\n\nSome prose.\n\n" + TABLE_BODY,
            2,
            id="blank-after-options",
        ),
        pytest.param("Cap", "continued\n\nnot a table", 0, id="no-table-follows"),
        pytest.param("Cap", "continued", 0, id="no-table-at-all"),
        pytest.param(
            "Cap", "continued\n\n| a | b |\n| 1 | 2 |", 0, id="no-delimiter-row"
        ),
        pytest.param("Cap", "\n" + TABLE_BODY, 1, id="table-only"),
        pytest.param(
            "Cap", "[x]: https://example.com\n\n" + TABLE_BODY, 0, id="link-definition"
        ),
        pytest.param(
            "Cap",
            "```{default-role} math\n```\n\n" + TABLE_BODY,
            0,
            id="directive-fence",
        ),
        pytest.param("Cap", "(label)=\n\n" + TABLE_BODY, 0, id="target"),
        pytest.param("Cap", "% comment\n\n" + TABLE_BODY, 0, id="comment"),
        pytest.param("Cap", "+++\n\n" + TABLE_BODY, 0, id="block-break"),
        pytest.param("Cap", "{.striped}\n" + TABLE_BODY, 0, id="attrs-class"),
        pytest.param("Cap", "{#mytbl}\n" + TABLE_BODY, 0, id="attrs-id"),
        pytest.param(
            "Cap", '{#mytbl .striped key="v"}\n' + TABLE_BODY, 0, id="attrs-mixed"
        ),
        pytest.param("", "{.striped}\n" + TABLE_BODY, 0, id="attrs-no-argument"),
        pytest.param(
            "Cap", ":name: x\n{.striped}\n" + TABLE_BODY, 1, id="attrs-after-options"
        ),
    ],
)
def test_table_body_not_folded(first_line, content, body_offset):
    """Lines are only folded into the caption if they directly follow the opening
    line (or the options block), contain no MyST block syntax, and a table follows;
    otherwise the body is left as it is.

    In particular, a paragraph separated from the opening line by a blank line
    is not a caption, so it still gives the "exactly one table expected" error,
    and a link definition or a block attributes line (which render nothing)
    can still precede the table.
    """
    result = parse_directive_text(RSTTable, first_line, content)
    assert result.arguments == ([first_line] if first_line else [])
    assert result.body_offset == body_offset
    assert result.body == content.splitlines()[body_offset:]
    assert not result.warnings


@pytest.mark.parametrize(
    "content,warning_line,options,body_offset",
    [
        pytest.param("continued\n:name: tbl\n\n" + TABLE_BODY, 3, {}, 0, id="option"),
        pytest.param(
            "continued\n:name: tbl\n" + TABLE_BODY, 3, {}, 0, id="option-no-blank"
        ),
        pytest.param(
            "continued\n---\nname: tbl\n---\n\n" + TABLE_BODY,
            3,
            {},
            0,
            id="yaml-block",
        ),
        # the warning line counts the options block before the caption line
        pytest.param(
            ":name: a\ncontinued\n:align: center\n\n" + TABLE_BODY,
            4,
            {"name": "a"},
            1,
            id="option-after-options-block",
        ),
    ],
)
def test_table_caption_with_options_after_it_warns(
    content, warning_line, options, body_offset
):
    """Options cannot follow wrapped caption lines: they would be silently lost
    in the caption, so the body is left unchanged (which then fails
    with "exactly one table expected") and a warning says where options go.
    """
    result = parse_directive_text(RSTTable, "Cap", content, line=1)
    assert result.arguments == ["Cap"]
    assert result.body == content.splitlines()[body_offset:]
    assert result.body_offset == body_offset
    assert result.options == options
    message = (
        "Options must directly follow the directive's opening line; "
        "place wrapped caption lines after the options block"
    )
    assert [(w.msg, w.lineno) for w in result.warnings] == [(message, warning_line)]


def test_table_delimiter_row_check_is_linear():
    """The delimiter-row check must not backtrack super-linearly:
    a line of spaces around a ``-`` once took cubic time
    (a 3 KB document took 10 seconds to parse).
    """
    spaces = " " * 3000
    content = "a | b\n" + spaces + "-" + spaces + "x"
    start = time.perf_counter()
    result = parse_directive_text(RSTTable, "Cap", content)
    assert time.perf_counter() - start < 1
    assert result.arguments == ["Cap"]
    assert result.body == content.splitlines()
    assert not result.warnings


def test_table_caption_on_one_line_unchanged():
    """A single-line caption is still the only argument, body is the table."""
    result = parse_directive_text(
        RSTTable,
        "Table caption",
        "\n" + TABLE_BODY,
    )
    assert result.arguments == ["Table caption"]
    assert result.body == TABLE_BODY.splitlines()
    assert result.body_offset == 1
