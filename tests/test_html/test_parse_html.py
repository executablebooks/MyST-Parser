from pathlib import Path

import pytest

from myst_parser.parsers.parse_html import tokenize_html

FIXTURE_PATH = Path(__file__).parent


@pytest.mark.param_file(FIXTURE_PATH / "html_ast.md")
def test_html_ast(file_params):
    tokens = "\n".join(
        repr(t) for t in tokenize_html(file_params.content).walk(include_self=True)
    )
    file_params.assert_expected(tokens, rstrip=True)


@pytest.mark.param_file(FIXTURE_PATH / "html_round_trip.md")
def test_html_round_trip(file_params):
    ast = tokenize_html(file_params.content)
    file_params.assert_expected(str(ast), rstrip=True)


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
