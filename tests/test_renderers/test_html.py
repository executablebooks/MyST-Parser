from textwrap import dedent

import pytest

from myst_parser import text_to_tokens, render_tokens, parse_text
from mistletoe.block_token import tokenize

from myst_parser.html_renderer import HTMLRenderer


@pytest.fixture
def renderer():
    renderer = HTMLRenderer()
    with renderer:
        yield renderer


def test_render_tokens():
    root = text_to_tokens("abc")
    assert render_tokens(root, HTMLRenderer) == "<p>abc</p>\n"


def test_math(renderer):
    output = renderer.render(tokenize(["$a=1$"])[0])
    assert output == dedent("<p>$$a=1$$</p>")


def test_role(renderer):
    output = renderer.render(tokenize(["{name}`content`"])[0])
    assert output == dedent('<p><span class="role" name="name">content</span></p>')


def test_directive(renderer):
    output = renderer.render(tokenize(["```{name} arg\n", "foo\n", "```\n"])[0])
    assert output == dedent(
        """\
        <div class="myst-directive">
        <pre><code>{name} arg
        foo
        </code></pre></span>
        </div>"""
    )


def test_block_break(renderer):
    output = renderer.render(text_to_tokens("+++ abc"))
    assert output.splitlines() == [
        "<!-- myst-block-data abc -->",
        '<hr class="myst-block-break" />',
    ]


def test_line_comment(renderer):
    output = renderer.render(tokenize([r"% abc"])[0])
    assert output == "<!-- abc -->"


def test_target():
    output = parse_text("(a)=", "html")
    assert output == (
        '<p><a class="myst-target" href="#a" title="Permalink to here">(a)=</a></p>\n'
    )


def test_front_matter(renderer):
    output = renderer.render(text_to_tokens("---\na: 1\nb: 2\nc: 3\n---"))
    assert output.splitlines() == [
        '<div class="myst-front-matter"><pre><code class="language-yaml">a: 1',
        "b: 2",
        "c: 3",
        "</code></pre></div>",
    ]
