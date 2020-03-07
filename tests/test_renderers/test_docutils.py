from textwrap import dedent
from unittest import mock

from mistletoe.block_tokenizer import tokenize_main
from mistletoe.span_tokenizer import tokenize_span

from myst_parser import text_to_tokens, render_tokens, parse_text
from myst_parser.block_tokens import Document
from myst_parser.docutils_renderer import SphinxRenderer


def render_token(
    renderer_mock, token_name, children=True, without_attrs=None, **kwargs
):
    render_func = renderer_mock.render_map[token_name]
    children = mock.MagicMock(spec=list) if children else None
    if "position" not in kwargs:
        kwargs["position"] = (0, 0)
    mock_token = mock.Mock(children=children, **kwargs)
    without_attrs = without_attrs or []
    for attr in without_attrs:
        delattr(mock_token, attr)
    render_func(mock_token)


def test_text_to_tokens():
    root = text_to_tokens("abc")
    document = render_tokens(
        root,
        SphinxRenderer,
        load_sphinx_env=True,
        sphinx_conf={"project": "MyST Parser"},
    )
    assert document.pformat() == (
        '<document source="notset">\n    <paragraph>\n        abc\n'
    )


def test_parse_text():
    document = parse_text(
        "abc", "sphinx", load_sphinx_env=True, sphinx_conf={"project": "MyST Parser"}
    )
    assert document.pformat() == (
        '<document source="notset">\n    <paragraph>\n        abc\n'
    )


def test_strong(renderer_mock):
    render_token(renderer_mock, "Strong")
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="notset">
        <strong>
    """
    )


def test_emphasis(renderer_mock):
    render_token(renderer_mock, "Emphasis")
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="notset">
        <emphasis>
    """
    )


def test_raw_text(renderer_mock):
    render_token(renderer_mock, "RawText", children=False, content="john & jane")
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="notset">
        john & jane
    """
    )


def test_inline_code(renderer_mock):
    renderer_mock.render(tokenize_span("`foo`")[0])
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="notset">
        <literal>
            foo
    """
    )


def test_paragraph(renderer_mock):
    render_token(renderer_mock, "Paragraph", position=(0, 1))
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="notset">
        <paragraph>
    """
    )


def test_heading(renderer_mock):
    render_token(renderer_mock, "Heading", level=1, position=(0, 0))
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="notset">
        <section ids="id1" names="">
            <title>
    """
    )


def test_block_code(renderer_mock):

    renderer_mock.render(tokenize_main(["```sh\n", "foo\n", "```\n"])[0])
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="notset">
        <literal_block language="sh" xml:space="preserve">
            foo
    """
    )


def test_block_code_no_language(renderer_mock):

    renderer_mock.render(tokenize_main(["```\n", "foo\n", "```\n"])[0])
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="notset">
        <literal_block language="" xml:space="preserve">
            foo
    """
    )


def test_image(renderer_mock):
    render_token(renderer_mock, "Image", src="src", title="title")
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="notset">
        <image alt="" uri="src">
    """
    )


def test_image_with_alt(renderer_mock):
    renderer_mock.render(tokenize_main([r"![alt](path/to/image.jpeg)"])[0])
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="notset">
        <paragraph>
            <image alt="alt" uri="path/to/image.jpeg">
    """
    )


def test_quote(renderer_mock):
    render_token(renderer_mock, "Quote", position=(0, 0))
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="notset">
        <block_quote>
    """
    )


def test_bullet_list(renderer_mock):
    render_token(renderer_mock, "List", start_at=None)
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="notset">
        <bullet_list>
    """
    )


def test_enumerated_list(renderer_mock):
    render_token(renderer_mock, "List", start_at=1)
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="notset">
        <enumerated_list>
    """
    )


def test_list_item(renderer_mock):
    render_token(renderer_mock, "ListItem")
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="notset">
        <list_item>
    """
    )


def test_math(renderer_mock):
    render_token(renderer_mock, "Math", content="$a$")
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="notset">
        <math>
            a
    """
    )


def test_math_block(renderer_mock):
    render_token(renderer_mock, "Math", content="$$a$$")
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="notset">
        <math_block nowrap="False" number="True" xml:space="preserve">
            a
    """
    )


def test_role_code(renderer_mock):
    renderer_mock.render(tokenize_span("{code}`` a=1{`} ``")[0])
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="notset">
        <literal classes="code">
            a=1{`}
    """
    )


def test_target_block(renderer_mock):
    renderer_mock.render(tokenize_main(["(target)="])[0])
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="notset">
        <target ids="target" names="target">
    """
    )


def test_target_inline(renderer_mock):
    renderer_mock.render(tokenize_main(["A b(target)="])[0])
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="notset">
        <paragraph>
            A b
            <target ids="target" names="target">
    """
    )


def test_cross_referencing(sphinx_renderer, file_regression):
    string = dedent(
        """\
        (target)=

        Title
        -----

        [alt1](target)

        [](target2)

        [alt2](https://www.google.com)

        [alt3](#target3)
        """
    )
    sphinx_renderer.render(Document.read(string))
    file_regression.check(sphinx_renderer.document.pformat(), extension=".xml")


def test_comment(renderer_mock):
    renderer_mock.render(tokenize_main([r"% a comment"])[0])
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="notset">
        <comment xml:space="preserve">
            a comment
    """
    )


def test_block_break(renderer_mock):
    renderer_mock.render(tokenize_main(["+++ string"])[0])
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="notset">
        <comment classes="block_break" xml:space="preserve">
            string
    """
    )


def test_link_reference(renderer):
    renderer.render(
        Document.read(
            ["[name][key]", "", '[key]: https://www.google.com "a title"', ""]
        )
    )
    assert renderer.document.pformat() == dedent(
        """\
    <document source="notset">
        <paragraph>
            <reference refuri="https://www.google.com" title="a title">
                name
    """
    )


def test_link_reference_no_key(renderer):
    renderer.render(
        Document.read(["[name]", "", '[name]: https://www.google.com "a title"', ""])
    )
    assert renderer.document.pformat() == dedent(
        """\
    <document source="notset">
        <paragraph>
            <reference refuri="https://www.google.com" title="a title">
                name
    """
    )


def test_block_quotes(renderer):
    renderer.render(
        Document.read(
            dedent(
                """\
            ```{epigraph}
            a b*c*

            -- a**b**
            """
            )
        )
    )
    assert renderer.document.pformat() == dedent(
        """\
    <document source="notset">
        <block_quote classes="epigraph">
            <paragraph>
                a b
                <emphasis>
                    c
            <attribution>
                a
                <strong>
                    b
    """
    )


def test_full_run(sphinx_renderer, file_regression):
    string = dedent(
        """\
        ---
        a: 1
        ---

        (target)=
        # header 1
        ## sub header 1

        a *b* **c** `abc` \\*

        ## sub header 2

        x y [a](http://www.xyz.com) z

        ---

        # header 2

        ```::python {a=1}
        a = 1
        ```

        > abc

        - a
        - b
            - c

        1. a
        2. b
            1. c

        {ref}`target`

        """
    )

    sphinx_renderer.render(Document.read(string))
    file_regression.check(sphinx_renderer.document.pformat(), extension=".xml")
