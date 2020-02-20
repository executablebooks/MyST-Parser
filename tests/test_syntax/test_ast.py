import pytest

from myst_parser.ast_renderer import AstRenderer
from myst_parser.block_tokens import Document


@pytest.fixture
def ast_renderer():
    renderer = AstRenderer()
    with renderer:
        yield renderer


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


@pytest.mark.parametrize("name,strings", [("basic", ["---", "a: b", "---"])])
def test_front_matter(name, ast_renderer, data_regression, strings):
    document = Document(strings)
    data_regression.check(ast_renderer.render(document))
