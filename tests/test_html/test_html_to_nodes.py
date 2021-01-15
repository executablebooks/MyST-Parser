from unittest.mock import Mock
import pytest

from myst_parser.html_to_nodes import html_to_nodes


@pytest.mark.parametrize("text", ["", "abc", "<div></div>" "<div><img></div>"])
def test_html_img_parse_none(text):
    document = Mock(reporter=Mock(error=Mock(return_value="error")))
    output = html_to_nodes(text, document, 0)
    assert output is None


@pytest.mark.parametrize(
    "text", ["<img>", '<img src="a" width="x">', '<img src="a" height="x">']
)
def test_html_img_parse_error(text):
    document = Mock(reporter=Mock(error=Mock(return_value="error")))
    output = html_to_nodes(text, document, 0)
    assert len(output) == 1
    assert output[0] == "error"


@pytest.mark.parametrize(
    "text,outcome",
    [
        ('<img src="a">', '<image uri="a">'),
        ('<img src="a" other="b">', '<image uri="a">'),
        (
            '<img src="a" height="200px" class="a b">',
            '<image classes="a b" height="200px" uri="a">',
        ),
        (
            '<img src="a" name="b" align="left">',
            '<image align="left" names="b" uri="a">',
        ),
    ],
)
def test_html_img_parse_ok(text, outcome):
    document = Mock(reporter=Mock(error=Mock(return_value="error")))
    output = html_to_nodes(text, document, 0)
    assert len(output) == 1
    assert output[0].pformat().strip() == outcome


def test_html_multi_img_parse_ok():
    text = '<img src="a">\n<img src="b">'
    outcome = ['<image uri="a">', '<image uri="b">']
    document = Mock(reporter=Mock(error=Mock(return_value="error")))
    output = html_to_nodes(text, document, 0)
    assert [o.pformat().strip() for o in output] == outcome
