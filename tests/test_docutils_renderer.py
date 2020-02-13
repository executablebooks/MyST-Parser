import json
import os
from textwrap import dedent, indent
from unittest import mock

import pytest

from mistletoe.block_token import tokenize
from mistletoe.span_token import tokenize_inner

from myst_parser.block_tokens import Document
from myst_parser.docutils_renderer import DocutilsRenderer


@pytest.fixture
def renderer():
    renderer = DocutilsRenderer()
    with renderer:
        yield renderer


@pytest.fixture
def renderer_mock():
    renderer = DocutilsRenderer()
    renderer.render_inner = mock.Mock(return_value="inner")
    with renderer:
        yield renderer


@pytest.fixture
def sphinx_renderer(renderer):
    from sphinx.util.docutils import docutils_namespace, sphinx_domains

    with docutils_namespace():
        app = renderer.mock_sphinx_env()
        with sphinx_domains(app.env):
            yield renderer


def render_token(
    renderer_mock, token_name, children=True, without_attrs=None, **kwargs
):
    render_func = renderer_mock.render_map[token_name]
    children = mock.MagicMock(spec=list) if children else None
    mock_token = mock.Mock(children=children, **kwargs)
    without_attrs = without_attrs or []
    for attr in without_attrs:
        delattr(mock_token, attr)
    render_func(mock_token)


def test_strong(renderer_mock):
    render_token(renderer_mock, "Strong")
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="">
        <strong>
    """
    )


def test_emphasis(renderer_mock):
    render_token(renderer_mock, "Emphasis")
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="">
        <emphasis>
    """
    )


def test_raw_text(renderer_mock):
    render_token(renderer_mock, "RawText", children=False, content="john & jane")
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="">
        john & jane
    """
    )


def test_inline_code(renderer_mock):
    renderer_mock.render(tokenize_inner("`foo`")[0])
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="">
        <literal>
            foo
    """
    )


def test_paragraph(renderer_mock):
    render_token(renderer_mock, "Paragraph", range=(0, 1))
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="">
        <paragraph>
    """
    )


def test_heading(renderer_mock):
    render_token(renderer_mock, "Heading", level=1, range=(0, 0))
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="">
        <section ids="id1" names="">
            <title>
    """
    )


def test_block_code(renderer_mock):

    renderer_mock.render(tokenize(["```sh\n", "foo\n", "```\n"])[0])
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="">
        <literal_block language="sh" xml:space="preserve">
            foo
    """
    )


def test_block_code_no_language(renderer_mock):

    renderer_mock.render(tokenize(["```\n", "foo\n", "```\n"])[0])
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="">
        <literal_block language="" xml:space="preserve">
            foo
    """
    )


def test_image(renderer_mock):
    render_token(renderer_mock, "Image", src="src", title="title")
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="">
        <image alt="" uri="src">
    """
    )


def test_image_with_alt(renderer_mock):
    renderer_mock.render(tokenize([r"![alt](path/to/image.jpeg)"])[0])
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="">
        <paragraph>
            <image alt="alt" uri="path/to/image.jpeg">
    """
    )


def test_quote(renderer_mock):
    render_token(renderer_mock, "Quote", range=(0, 0))
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="">
        <block_quote>
    """
    )


def test_bullet_list(renderer_mock):
    render_token(renderer_mock, "List", start=None)
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="">
        <bullet_list>
    """
    )


def test_enumerated_list(renderer_mock):
    render_token(renderer_mock, "List", start=1)
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="">
        <enumerated_list>
    """
    )


def test_list_item(renderer_mock):
    render_token(renderer_mock, "ListItem")
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="">
        <list_item>
    """
    )


def test_math(renderer_mock):
    render_token(renderer_mock, "Math", content="$a$")
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="">
        <math>
            a
    """
    )


def test_math_block(renderer_mock):
    render_token(renderer_mock, "Math", content="$$a$$")
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="">
        <math_block nowrap="False" number="True" xml:space="preserve">
            a
    """
    )


def test_role_code(renderer_mock):
    renderer_mock.render(tokenize_inner("{code}`` a=1{`} ``")[0])
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="">
        <literal classes="code">
            a=1{`}
    """
    )


def test_target_block(renderer_mock):
    renderer_mock.render(tokenize(["(target)="])[0])
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="">
        <target ids="target" names="target">
    """
    )


def test_target_inline(renderer_mock):
    renderer_mock.render(tokenize(["A b(target)="])[0])
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="">
        <paragraph>
            A b
            <target ids="target" names="target">
    """
    )


def test_comment(renderer_mock):
    renderer_mock.render(tokenize([r"% a comment"])[0])
    assert renderer_mock.document.pformat() == dedent(
        """\
    <document source="">
        <comment xml:space="preserve">
            a comment
    """
    )


def test_footnote(renderer):
    renderer.render(
        Document(["[name][key]", "", '[key]: https://www.google.com "a title"', ""])
    )
    assert renderer.document.pformat() == dedent(
        """\
    <document source="">
        <paragraph>
            <reference refuri="https://www.google.com" title="a title">
                name
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

    sphinx_renderer.render(Document(string))
    file_regression.check(sphinx_renderer.document.pformat(), extension=".xml")


with open(os.path.join(os.path.dirname(__file__), "sphinx_roles.json"), "r") as fin:
    roles_tests = json.load(fin)


@pytest.mark.parametrize(
    "role_data",
    [
        r
        for r in roles_tests
        if r["import"].startswith("docutils")
        and not r["import"].endswith("unimplemented_role")
        and not r["import"].endswith("CustomRole")
    ],
)
def test_docutils_roles(renderer, role_data):
    """"""
    name = role_data["name"]
    if name in ["raw"]:
        # TODO fix skips
        pytest.skip("awaiting fix")
    text = "{{{0}}}`{1}`".format(name, role_data.get("content", " "))
    print(text)
    renderer.render(tokenize([text])[0])
    print(
        repr(renderer.document.pformat()).replace(" " * 8, "    ").replace('"', '\\"')
    )
    assert renderer.document.pformat() == (
        role_data.get("doc_tag", '<document source="">')
        + "\n"
        + indent(role_data["output"], "    ")
        + ("\n" if role_data["output"] else "")
    )


@pytest.mark.parametrize(
    "role_data",
    [
        r
        for r in roles_tests
        if r["import"].startswith("sphinx")
        # and not r["import"].endswith("unimplemented_role")
        # and not r["import"].endswith("CustomRole")
    ],
)
def test_sphinx_roles(sphinx_renderer, role_data):
    """"""
    name = role_data["name"]
    # note, I think most of these have are actually node types rather than roles,
    # that I've erroneously picked up in my gather function.
    if name in [
        "c:function",
        "c:var",
        "cpp:function",
        "cpp:namespace",
        "cpp:alias",
        "cpp:namespace-pop",
        "cpp:namespace-push",
        "cpp:enum-struct",
        "cpp:enum-class",
        "js:function",
        "js:method",
        "js:attribute",
        "js:module",
        "py:function",
        "py:exception",
        "py:method",
        "py:classmethod",
        "py:staticmethod",
        "py:attribute",
        "py:module",
        "py:currentmodule",
        "py:decorator",
        "py:decoratormethod",
        "rst:directive",
        "rst:directive:option",
        "envvar",
        "cmdoption",
        "glossary",
        "productionlist",
        "abbr",
    ]:
        # TODO fix skips
        pytest.skip("awaiting fix")
    sphinx_renderer.render(
        tokenize(["{{{}}}`{}`".format(name, role_data.get("content", "a"))])[0]
    )
    print(
        repr(sphinx_renderer.document.pformat())
        .replace(" " * 8, "    ")
        .replace('"', '\\"')
    )
    assert sphinx_renderer.document.pformat() == (
        role_data.get("doc_tag", '<document source="">')
        + "\n"
        + indent(role_data["output"], "    ")
        + ("\n" if role_data["output"] else "")
    )


with open(
    os.path.join(os.path.dirname(__file__), "sphinx_directives.json"), "r"
) as fin:
    directive_tests = json.load(fin)


@pytest.mark.parametrize(
    "directive",
    [
        d
        for d in directive_tests
        if d["class"].startswith("docutils") and not d.get("sub_only", False)
        # todo add substitution definition directive and reference role
    ],
)
def test_docutils_directives(renderer, directive):
    """See https://docutils.sourceforge.io/docs/ref/rst/directives.html"""
    name = directive["name"]
    if name in ["role", "rst-class", "cssclass", "line-block"]:
        # TODO fix skips
        pytest.skip("awaiting fix")
    arguments = " ".join(directive["args"])
    renderer.render(
        tokenize(
            [
                "```{{{}}} {}\n".format(name, arguments),
                directive.get("content", "") + "\n",
                "```\n",
            ]
        )[0]
    )
    print(
        repr(renderer.document.pformat()).replace(" " * 8, "    ").replace('"', '\\"')
    )
    assert renderer.document.pformat() == (
        directive.get("doc_tag", '<document source="">')
        + "\n"
        + indent(directive["output"], "    ")
        + ("\n" if directive["output"] else "")
    )


@pytest.mark.parametrize(
    "directive",
    [
        d
        for d in directive_tests
        if d["class"].startswith("sphinx") and not d.get("sub_only", False)
    ],
)
def test_sphinx_directives(sphinx_renderer, directive):
    """See https://docutils.sourceforge.io/docs/ref/rst/directives.html"""
    name = directive["name"]
    if name in ["csv-table", "meta", "include"]:
        # TODO fix skips
        pytest.skip("awaiting fix")
    arguments = " ".join(directive["args"])
    sphinx_renderer.render(
        tokenize(
            [
                "```{{{}}} {}\n".format(name, arguments),
                directive.get("content", "") + "\n",
                "```\n",
            ]
        )[0]
    )
    print(
        repr(sphinx_renderer.document.pformat())
        .replace(" " * 8, "    ")
        .replace('"', '\\"')
    )
    assert sphinx_renderer.document.pformat() == (
        directive.get("doc_tag", '<document source="">')
        + "\n"
        + indent(directive["output"], "    ")
        + ("\n" if directive["output"] else "")
    )
