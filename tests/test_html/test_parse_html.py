from pathlib import Path

import pytest

from markdown_it.utils import read_fixture_file
from myst_parser.parse_html import tokenize_html

FIXTURE_PATH = Path(__file__).parent


@pytest.mark.parametrize(
    "line,title,text,expected",
    read_fixture_file(FIXTURE_PATH / "html_ast.md"),
    ids=[f"{i[0]}-{i[1]}" for i in read_fixture_file(FIXTURE_PATH / "html_ast.md")],
)
def test_html_ast(line, title, text, expected):
    tokens = "\n".join(repr(t) for t in tokenize_html(text).walk(include_self=True))
    try:
        assert tokens.rstrip() == expected.rstrip()
    except AssertionError:
        print(tokens)
        raise


@pytest.mark.parametrize(
    "line,title,text,expected",
    read_fixture_file(FIXTURE_PATH / "html_round_trip.md"),
    ids=[
        f"{i[0]}-{i[1]}" for i in read_fixture_file(FIXTURE_PATH / "html_round_trip.md")
    ],
)
def test_html_round_trip(line, title, text, expected):
    ast = tokenize_html(text)
    try:
        assert str(ast).rstrip() == expected.rstrip()
    except AssertionError:
        print(str(ast))
        raise


def test_render_overrides():
    text = "<div><abc></abc></div>"
    ast = tokenize_html(text)

    def _render_abc(element, *args, **kwargs):
        return "hallo"

    output = ast.render(tag_overrides={"abc": _render_abc})
    assert output == "<div>hallo</div>"


def test_ast_find():
    text = (
        '<div class="a"><div class="c"><x/><y>z</y><div class="a b"></div></div></div>'
    )
    ast = tokenize_html(text)
    found = list(ast.find("div", classes=["a"]))
    assert [e.attrs.classes for e in found] == [["a"], ["a", "b"]]
