from textwrap import dedent

import pytest

from myst_parser import text_to_tokens, block_tokens, traverse
from myst_parser.ast_renderer import AstRenderer
from myst_parser.block_tokens import Document


@pytest.fixture
def ast_renderer():
    renderer = AstRenderer()
    with renderer:
        yield renderer


def test_render_tokens():
    root = text_to_tokens("abc")
    assert isinstance(root, Document)
    assert root.children, root.children


def test_traverse(ast_renderer):
    doc = Document(
        dedent(
            """\
        a **b**

        c [*d*](link)
        """
        )
    )
    tree = [
        (t.node.__class__.__name__, t.parent.__class__.__name__, t.depth)
        for t in traverse(doc)
    ]
    assert tree == [
        ("Paragraph", "Document", 1),
        ("Paragraph", "Document", 1),
        ("RawText", "Paragraph", 2),
        ("Strong", "Paragraph", 2),
        ("RawText", "Paragraph", 2),
        ("Link", "Paragraph", 2),
        ("RawText", "Strong", 3),
        ("Emphasis", "Link", 3),
        ("RawText", "Emphasis", 4),
    ]


@pytest.mark.parametrize(
    "token,args,repr_str",
    [
        (block_tokens.HTMLBlock, ([],), "MyST.HTMLBlock()"),
        (block_tokens.LineComment, (("", "%", 0),), "MyST.LineComment(range=(0, 0))"),
        (
            block_tokens.BlockCode,
            ([[], (1, 3)],),
            "MyST.BlockCode(range=(1, 3),language=none)",
        ),
        (
            block_tokens.Heading,
            ([2, "abc", (4, 5)],),
            "MyST.Heading(range=(4, 5),level=2)",
        ),
        (block_tokens.Quote, ([[], (1, 2)],), "MyST.Quote(range=(1, 2),children=0)"),
        (
            block_tokens.CodeFence,
            ([[], [None, None, "python", "\n"], (8, 9)],),
            "MyST.CodeFence(range=(8, 9),language=python)",
        ),
        (block_tokens.ThematicBreak, (["---", 6],), "MyST.ThematicBreak(range=(6, 6))"),
        (
            block_tokens.BlockBreak,
            (["abc", "+++ abc", 2],),
            "MyST.BlockBreak(range=(2, 2))",
        ),
        # TODO commented out tests
        # (block_tokens.List, ([],), ""),
        (
            block_tokens.Table,
            ([["a", "---", "b"], (0, 3)],),
            "MyST.Table(range=(0, 3),rows=1)",
        ),
        (
            block_tokens.TableRow,
            ("abc | xyz", 4),
            "MyST.TableRow(range=[4, 4],cells=2)",
        ),
        (block_tokens.LinkDefinition, ([],), "None"),
        (
            block_tokens.FrontMatter,
            (["---", "a: b", "---"],),
            "MyST.FrontMatter(range=(0, 3))",
        ),
        (
            block_tokens.Paragraph,
            ([[], (0, 0)],),
            "MyST.Paragraph(range=(0, 0),children=0)",
        ),
    ],
)
def test_repr(token, args, repr_str):
    print(token(*args))
    assert repr(token(*args)) == repr_str


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
def test_role(name, ast_renderer, data_regression, strings):
    document = Document(strings)
    data_regression.check(ast_renderer.render(document))


@pytest.mark.parametrize(
    "name,strings",
    [
        ("basic", ["$a$"]),
        ("contains_special_chars", ["$a`{_*-%$"]),
        ("preceding_special_chars", ["{_*-%`$a$"]),
        ("multiple", ["$a$ $b$"]),
        ("escaped_opening", ["\\$a $b$"]),
        ("no_closing", ["$a"]),
        ("internal_emphasis", ["$*a*$"]),
        ("external_emphasis", ["*$a$*"]),
        ("multiline", ["$$a", "c", "b$$"]),
        (
            "issue_51",
            [
                "Math can be called in-line with single `$` characters around math.",
                "For example, `$x_{hey}=it+is^{math}$` renders $x_{hey}=it+is^{math}$.",
            ],
        ),
        ("in_link_content", ["[$a$](link)"]),
        ("in_link_target", ["[a]($b$)"]),
        ("in_image", ["![$a$]($b$)"]),
    ],
)
def test_math(name, ast_renderer, data_regression, strings):
    document = Document(strings)
    data_regression.check(ast_renderer.render(document))


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
def test_target(name, ast_renderer, data_regression, strings):
    document = Document(strings)
    data_regression.check(ast_renderer.render(document))


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
def test_comment(name, ast_renderer, data_regression, strings):
    document = Document(strings)
    data_regression.check(ast_renderer.render(document))


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
def test_block_break(name, ast_renderer, data_regression, strings):
    document = Document(strings)
    data_regression.check(ast_renderer.render(document))


@pytest.mark.parametrize("name,strings", [("basic", ["---", "a: b", "---"])])
def test_front_matter(name, ast_renderer, data_regression, strings):
    document = Document(strings)
    data_regression.check(ast_renderer.render(document))


@pytest.mark.parametrize(
    "name,strings",
    [
        ("ref_first", ["[ref]", "", '[ref]: https://google.com "title"']),
        ("ref_last", ['[ref]: https://google.com "title"', "", "[ref]"]),
        ("ref_syntax", ["[*syntax*]", "", '[*syntax*]: https://google.com "title"']),
        ("ref_escape", ["[ref]", "", '\\[ref]: https://google.com "title"']),
    ],
)
def test_link_references(name, strings, ast_renderer, data_regression):
    document = Document(strings)
    data_regression.check(ast_renderer.render(document))


def test_table(ast_renderer, data_regression):
    string = dedent(
        """\
        | abc | d   | e     |
        | --- | --- | :---: |
        | hjk | *y* | z     |
        """
    )
    document = Document(string)
    data_regression.check(ast_renderer.render(document))
