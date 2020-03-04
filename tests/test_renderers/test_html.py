from textwrap import dedent

import pytest

from myst_parser import text_to_tokens, render_tokens
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
    <pre><code class="language-{name}">foo
    </code></pre>"""
    )
