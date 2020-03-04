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
    assert output == (
        '<p><span class="myst-role"><code>{name}content</code></span></p>'
    )


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


def test_minimal_html_page(file_regression):
    in_string = dedent(
        """\
        ---
        a: 1
        ---
        (title-target)=
        # title

        Abc $a=1$ {role}`content` then more text

        +++ my break

        ```{directive} args
        :option: 1
        content
        ```

        ```python
        def func(a):
            print("{}".format(a))
        ```

        % a comment

        [link to target](#title-target)
        """
    )

    out_string = parse_text(
        in_string,
        "html",
        add_mathjax=True,
        as_standalone=True,
        add_css=dedent(
            """\
            div.myst-front-matter {
                border: 1px solid gray;
            }
            div.myst-directive {
                background: lightgreen;
            }
            hr.myst-block-break {
                border-top:1px dotted black;
            }
            span.myst-role {
                background: lightgreen;
            }
            """
        ),
    )
    file_regression.check(out_string, extension=".html")
