import json
from pathlib import Path

import pytest
import yaml
from docutils.parsers.rst.directives.admonitions import Admonition, Note
from docutils.parsers.rst.directives.body import Rubric
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
