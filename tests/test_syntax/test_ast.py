from textwrap import dedent

import pytest

from myst_parser import text_to_tokens
from myst_parser.json_renderer import JsonRenderer
from myst_parser.block_tokens import Document


@pytest.fixture
def json_renderer():
    renderer = JsonRenderer()
    with renderer:
        yield renderer


def test_render_tokens():
    root = text_to_tokens("abc")
    assert isinstance(root, Document)
    assert root.children, root.children


def test_walk(json_renderer, data_regression):
    doc = Document.read(
        dedent(
            """\
        a **b**

        c [*d*](link)
        """
        )
    )
    tree = [(repr(t.node), repr(t.parent), t.depth) for t in doc.walk()]
    data_regression.check(tree)


@pytest.mark.parametrize(
    "name,strings",
    [
        ("basic", ["{name}`some content`"]),
        ("indent_2", ["  {name}`some content`"]),
        ("indent_4", ["    {name}`some econtent`"]),
        ("escaped", ["\\{name}`some content`"]),
        ("inline", ["a {name}`some content`"]),
        ("multiple", ["{name}`some content`  {name2}`other`"]),
        ("internal_emphasis", ["{name}`*content*`"]),
        ("external_emphasis", ["*{name}`content`*"]),
        ("internal_math", ["{name}`some $content$`"]),
        ("external_math", ["${name}`some content`$"]),
        ("internal_code", ["{name}` ``some content`` `"]),
        ("external_code", ["`` {name}`some content` ``"]),
    ],
)
def test_role(name, json_renderer, data_regression, strings):
    document = Document.read(strings)
    data_regression.check(json_renderer.render(document, as_string=False))


@pytest.mark.parametrize(
    "name,strings",
    [
        ("basic", ["(target)="]),
        ("indent_2", ["  (target)="]),
        ("indent_4", ["    (target)="]),
        ("escaped", ["\\(target)="]),
        ("inline", ["a (target)="]),
        ("internal_emphasis", ["(*target*)="]),
        ("external_emphasis", ["*(target)=*"]),
    ],
)
def test_target(name, json_renderer, data_regression, strings):
    document = Document.read(strings)
    data_regression.check(json_renderer.render(document, as_string=False))


@pytest.mark.parametrize(
    "name,strings",
    [
        ("basic", [r"% comment"]),
        ("indent_2", [r"  % comment"]),
        ("indent_4", [r"    % comment"]),
        ("escaped", [r"\% comment"]),
        ("inline", [r"a % comment"]),
        ("follows_list", ["- item", r"% comment"]),
    ],
)
def test_comment(name, json_renderer, data_regression, strings):
    document = Document.read(strings)
    data_regression.check(json_renderer.render(document, as_string=False))


@pytest.mark.parametrize(
    "name,strings",
    [
        ("basic", ["+++"]),
        ("indent_2", ["  +++"]),
        ("indent_4", ["    +++"]),
        ("escaped", [r"\+++"]),
        ("inline", ["a +++"]),
        ("following_content", ["+++ a"]),
        ("following_space", ["+++   "]),
        ("follows_list", ["- item", "+++"]),
        ("following_content_no_space", ["+++a"]),
    ],
)
def test_block_break(name, json_renderer, data_regression, strings):
    document = Document.read(strings)
    data_regression.check(json_renderer.render(document, as_string=False))


@pytest.mark.parametrize("name,strings", [("basic", ["---", "a: b", "---"])])
def test_front_matter(name, json_renderer, data_regression, strings):
    document = Document.read(strings)
    data_regression.check(json_renderer.render(document, as_string=False))


@pytest.mark.parametrize(
    "name,strings",
    [
        ("ref_first", ["[ref]", "", '[ref]: https://google.com "title"']),
        ("ref_last", ['[ref]: https://google.com "title"', "", "[ref]"]),
        ("ref_syntax", ["[*syntax*]", "", '[*syntax*]: https://google.com "title"']),
        ("ref_escape", ["[ref]", "", '\\[ref]: https://google.com "title"']),
    ],
)
def test_link_references(name, strings, json_renderer, data_regression):
    document = Document.read(strings)
    data_regression.check(json_renderer.render(document, as_string=False))


def test_table(json_renderer, data_regression):
    string = dedent(
        """\
        | abc | d   | e     |
        | --- | --- | :---: |
        | hjk | *y* | z     |
        """
    )
    document = Document.read(string)
    data_regression.check(json_renderer.render(document, as_string=False))
