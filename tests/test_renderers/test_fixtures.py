from pathlib import Path

import pytest

from markdown_it.utils import read_fixture_file
from myst_parser.main import to_docutils
from myst_parser.sphinx_renderer import mock_sphinx_env

FIXTURE_PATH = Path(__file__).parent.joinpath("fixtures")


def test_minimal_sphinx():
    with mock_sphinx_env(conf={"author": "bob geldof"}) as app:
        assert app.config["author"] == "bob geldof"


@pytest.mark.parametrize(
    "line,title,input,expected",
    read_fixture_file(FIXTURE_PATH.joinpath("syntax_elements.md")),
)
def test_syntax_elements(line, title, input, expected):
    document = to_docutils(input, in_sphinx_env=True)
    print(document.pformat())
    assert "\n".join(
        [ll.rstrip() for ll in document.pformat().splitlines()]
    ) == "\n".join([ll.rstrip() for ll in expected.splitlines()])


@pytest.mark.parametrize(
    "line,title,input,expected", read_fixture_file(FIXTURE_PATH.joinpath("tables.md"))
)
def test_tables(line, title, input, expected):
    document = to_docutils(input, in_sphinx_env=True)
    print(document.pformat())
    assert "\n".join(
        [ll.rstrip() for ll in document.pformat().splitlines()]
    ) == "\n".join([ll.rstrip() for ll in expected.splitlines()])


@pytest.mark.parametrize(
    "line,title,input,expected",
    read_fixture_file(FIXTURE_PATH.joinpath("directive_options.md")),
)
def test_directive_options(line, title, input, expected):
    document = to_docutils(input)
    print(document.pformat())
    assert "\n".join(
        [ll.rstrip() for ll in document.pformat().splitlines()]
    ) == "\n".join([ll.rstrip() for ll in expected.splitlines()])


@pytest.mark.parametrize(
    "line,title,input,expected",
    read_fixture_file(FIXTURE_PATH.joinpath("docutil_roles.md")),
)
def test_docutils_roles(line, title, input, expected):
    document = to_docutils(input)
    print(document.pformat())
    assert "\n".join(
        [ll.rstrip() for ll in document.pformat().splitlines()]
    ) == "\n".join([ll.rstrip() for ll in expected.splitlines()])


@pytest.mark.parametrize(
    "line,title,input,expected",
    read_fixture_file(FIXTURE_PATH.joinpath("docutil_directives.md")),
)
def test_docutils_directives(line, title, input, expected):
    # TODO fix skipped directives
    # TODO test domain directives
    if title.startswith("SKIP"):
        pytest.skip(title)
    document = to_docutils(input)
    print(document.pformat())
    assert "\n".join(
        [ll.rstrip() for ll in document.pformat().splitlines()]
    ) == "\n".join([ll.rstrip() for ll in expected.splitlines()])


@pytest.mark.parametrize(
    "line,title,input,expected",
    read_fixture_file(FIXTURE_PATH.joinpath("sphinx_directives.md")),
)
def test_sphinx_directives(line, title, input, expected):
    # TODO fix skipped directives
    # TODO test domain directives
    if title.startswith("SKIP"):
        pytest.skip(title)
    document = to_docutils(input, in_sphinx_env=True)
    print(document.pformat())
    assert "\n".join(
        [ll.rstrip() for ll in document.pformat().splitlines()]
    ) == "\n".join([ll.rstrip() for ll in expected.splitlines()])


@pytest.mark.parametrize(
    "line,title,input,expected",
    read_fixture_file(FIXTURE_PATH.joinpath("sphinx_roles.md")),
)
def test_sphinx_roles(line, title, input, expected):
    if title.startswith("SKIP"):
        pytest.skip(title)
    document = to_docutils(input, in_sphinx_env=True)
    print(document.pformat())
    assert "\n".join(
        [ll.rstrip() for ll in document.pformat().splitlines()]
    ) == "\n".join([ll.rstrip() for ll in expected.splitlines()])
