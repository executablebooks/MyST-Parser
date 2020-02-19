"""In this module, parsing of role and directive blocks are tested.

Tests are run against all roles/directives implemented internally in
docutils (v0.15) and sphinx (v2.1).
"""
import json
import os
import sys
from textwrap import dedent, indent

import pytest

from mistletoe.block_token import tokenize

from myst_parser.block_tokens import Document


@pytest.mark.parametrize(
    "name,arguments,body",
    [
        ("no_arg_no_content", "", False),
        ("no_arg_with_content", "", True),
        ("one_arg_no_content", "a", False),
        ("one_arg_with_content", "a", True),
        ("two_arg_no_content", "a b", False),
        ("two_arg_with_content", "a b", True),
    ],
)
def test_directive_arguments(renderer, name, arguments, body):
    content = (
        [
            "```{restructuredtext-test-directive}"
            + (" " if arguments else "")
            + arguments
        ]
        + (["content"] if body else [])
        + ["```"]
    )
    renderer.render(Document(content))
    expected = [
        '<document source="">',
        '    <system_message level="1" line="0" source="" type="INFO">',
        "        <paragraph>",
        (
            '            Directive processed. Type="restructuredtext-test-directive", '
            "arguments={args}, options={{}}, content:{content}".format(
                args=[arguments] if arguments else [], content="" if body else " None"
            )
        ),
    ]
    if body:
        expected.extend(
            ['        <literal_block xml:space="preserve">', "            content"]
        )
    expected.append("")
    assert renderer.document.pformat() == "\n".join(expected)


@pytest.mark.parametrize(
    "type,text", [("no_init_space", ("content",)), ("with_init_space", ("", "content"))]
)
def test_directive_no_options(renderer, type, text):
    renderer.render(
        Document(["```{restructuredtext-test-directive}"] + list(text) + ["```"])
    )
    assert renderer.document.pformat() == dedent(
        """\
    <document source="">
        <system_message level="1" line="0" source="" type="INFO">
            <paragraph>
                Directive processed. Type="restructuredtext-test-directive", arguments=[], options={}, content:
            <literal_block xml:space="preserve">
                content
    """  # noqa: E501
    )


@pytest.mark.skipif(
    sys.version_info.major == 3 and sys.version_info.minor <= 5,
    reason="option dict keys in wrong order",
)
@pytest.mark.parametrize(
    "type,text",
    [
        ("block_style", ("---", "option1: a", "option2: b", "---", "", "content")),
        ("colon_style", (":option1: a", ":option2: b", "", "content")),
        ("block_style_no_space", ("---", "option1: a", "option2: b", "---", "content")),
        ("colon_style_no_space", (":option1: a", ":option2: b", "content")),
    ],
)
def test_directive_options(renderer, type, text):
    renderer.render(
        Document(["```{restructuredtext-test-directive}"] + list(text) + ["```"])
    )
    assert renderer.document.pformat() == dedent(
        """\
    <document source="">
        <system_message level="1" line="0" source="" type="INFO">
            <paragraph>
                Directive processed. Type="restructuredtext-test-directive", arguments=[], options={'option1': 'a', 'option2': 'b'}, content:
            <literal_block xml:space="preserve">
                content
    """  # noqa: E501
    )


@pytest.mark.parametrize(
    "type,text",
    [
        ("block_style", ("---", "option1", "option2: b", "---", "", "content")),
        ("colon_style", (":option1", ":option2: b", "", "content")),
    ],
)
def test_directive_options_error(renderer, type, text):
    renderer.render(
        Document(["```{restructuredtext-test-directive}"] + list(text) + ["```"])
    )
    assert renderer.document.pformat() == dedent(
        """\
        <document source="">
            <system_message level="3" line="0" source="" type="ERROR">
                <paragraph>
                    Directive options:
                    mapping values are not allowed here
                      in "<unicode string>", line 2, column 8:
                        option2: b
                               ^
                <literal_block xml:space="preserve">
                    option1
                    option2: b
        """
    )


with open(os.path.join(os.path.dirname(__file__), "sphinx_roles.json"), "r") as fin:
    roles_tests = json.load(fin)


@pytest.mark.parametrize(
    "name,role_data",
    [
        (r["name"], r)
        for r in roles_tests
        if r["import"].startswith("docutils")
        and not r["import"].endswith("unimplemented_role")
        and not r["import"].endswith("CustomRole")
    ],
)
def test_docutils_roles(renderer, name, role_data):
    """"""
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
    "name,role_data",
    [
        (r["name"], r)
        for r in roles_tests
        if r["import"].startswith("sphinx")
        # and not r["import"].endswith("unimplemented_role")
        # and not r["import"].endswith("CustomRole")
    ],
)
def test_sphinx_roles(sphinx_renderer, name, role_data):
    """"""
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
    "name,directive",
    [
        (d["name"], d)
        for d in directive_tests
        if d["class"].startswith("docutils") and not d.get("sub_only", False)
        # todo add substitution definition directive and reference role
    ],
)
def test_docutils_directives(renderer, name, directive):
    """See https://docutils.sourceforge.io/docs/ref/rst/directives.html"""
    if name in [
        "role",
        "rst-class",
        "cssclass",
        "line-block",
        "block_quote",  # this is only used as a base class
    ]:
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
    "name,directive",
    [
        (d["name"], d)
        for d in directive_tests
        if d["class"].startswith("sphinx") and not d.get("sub_only", False)
    ],
)
def test_sphinx_directives(sphinx_renderer, name, directive):
    """See https://docutils.sourceforge.io/docs/ref/rst/directives.html"""
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
