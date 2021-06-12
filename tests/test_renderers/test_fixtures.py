import re
from pathlib import Path

import pytest
import sphinx
from markdown_it.utils import read_fixture_file

from myst_parser.main import MdParserConfig, to_docutils
from myst_parser.sphinx_renderer import SphinxRenderer, mock_sphinx_env

FIXTURE_PATH = Path(__file__).parent.joinpath("fixtures")


def test_minimal_sphinx():
    with mock_sphinx_env(conf={"author": "bob geldof"}, with_builder=True) as app:
        assert app.config["author"] == "bob geldof"


@pytest.mark.parametrize(
    "line,title,input,expected",
    read_fixture_file(FIXTURE_PATH.joinpath("syntax_elements.md")),
    ids=[
        f"{i[0]}-{i[1]}" for i in read_fixture_file(FIXTURE_PATH / "syntax_elements.md")
    ],
)
def test_syntax_elements(line, title, input, expected):
    document = to_docutils(input, in_sphinx_env=True)
    print(document.pformat())
    assert "\n".join(
        [ll.rstrip() for ll in document.pformat().splitlines()]
    ) == "\n".join([ll.rstrip() for ll in expected.splitlines()])


@pytest.mark.parametrize(
    "line,title,input,expected",
    read_fixture_file(FIXTURE_PATH.joinpath("tables.md")),
    ids=[f"{i[0]}-{i[1]}" for i in read_fixture_file(FIXTURE_PATH / "tables.md")],
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
    ids=[
        f"{i[0]}-{i[1]}"
        for i in read_fixture_file(FIXTURE_PATH / "directive_options.md")
    ],
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
    ids=[
        f"{i[0]}-{i[1]}" for i in read_fixture_file(FIXTURE_PATH / "docutil_roles.md")
    ],
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
    ids=[
        f"{i[0]}-{i[1]}"
        for i in read_fixture_file(FIXTURE_PATH / "docutil_directives.md")
    ],
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
    ids=[
        f"{i[0]}-{i[1]}"
        for i in read_fixture_file(FIXTURE_PATH / "sphinx_directives.md")
    ],
)
def test_sphinx_directives(line, title, input, expected):
    # TODO fix skipped directives
    # TODO test domain directives
    if title.startswith("SKIP"):
        pytest.skip(title)
    elif title.startswith("SPHINX3") and sphinx.version_info[0] < 3:
        pytest.skip(title)
    elif title.startswith("SPHINX4") and sphinx.version_info[0] < 4:
        pytest.skip(title)
    document = to_docutils(input, in_sphinx_env=True)
    _actual, _expected = [
        "\n".join([ll.rstrip() for ll in text.splitlines()])
        for text in (document.pformat(), expected)
    ]
    try:
        assert _actual == _expected
    except AssertionError:
        print(document.pformat())
        raise


@pytest.mark.parametrize(
    "line,title,input,expected",
    read_fixture_file(FIXTURE_PATH.joinpath("sphinx_roles.md")),
    ids=[f"{i[0]}-{i[1]}" for i in read_fixture_file(FIXTURE_PATH / "sphinx_roles.md")],
)
def test_sphinx_roles(line, title, input, expected):
    if title.startswith("SKIP"):
        pytest.skip(title)
    elif title.startswith("SPHINX4") and sphinx.version_info[0] < 4:
        pytest.skip(title)
    document = to_docutils(input, in_sphinx_env=True)
    print(document.pformat())
    _actual, _expected = [
        "\n".join([ll.rstrip() for ll in text.splitlines()])
        for text in (document.pformat(), expected)
    ]
    # sphinx 3 adds a parent key
    _actual = re.sub('cpp:parent_key="[^"]*"', 'cpp:parent_key=""', _actual)
    assert _actual == _expected


@pytest.mark.parametrize(
    "line,title,input,expected",
    read_fixture_file(FIXTURE_PATH.joinpath("amsmath.md")),
    ids=[f"{i[0]}-{i[1]}" for i in read_fixture_file(FIXTURE_PATH / "amsmath.md")],
)
def test_amsmath(line, title, input, expected, monkeypatch):
    monkeypatch.setattr(SphinxRenderer, "_random_label", lambda self: "mock-uuid")
    document = to_docutils(
        input, MdParserConfig(enable_extensions=["amsmath"]), in_sphinx_env=True
    )
    print(document.pformat())
    _actual, _expected = [
        "\n".join([ll.rstrip() for ll in text.splitlines()])
        for text in (document.pformat(), expected)
    ]
    assert _actual == _expected


@pytest.mark.parametrize(
    "line,title,input,expected",
    read_fixture_file(FIXTURE_PATH.joinpath("containers.md")),
    ids=[f"{i[0]}-{i[1]}" for i in read_fixture_file(FIXTURE_PATH / "containers.md")],
)
def test_containers(line, title, input, expected, monkeypatch):
    monkeypatch.setattr(SphinxRenderer, "_random_label", lambda self: "mock-uuid")
    document = to_docutils(
        input, MdParserConfig(enable_extensions=["colon_fence"]), in_sphinx_env=True
    )
    print(document.pformat())
    _actual, _expected = [
        "\n".join([ll.rstrip() for ll in text.splitlines()])
        for text in (document.pformat(), expected)
    ]
    assert _actual == _expected


@pytest.mark.parametrize(
    "line,title,input,expected",
    read_fixture_file(FIXTURE_PATH.joinpath("eval_rst.md")),
    ids=[f"{i[0]}-{i[1]}" for i in read_fixture_file(FIXTURE_PATH / "eval_rst.md")],
)
def test_evalrst_elements(line, title, input, expected):
    document = to_docutils(input, in_sphinx_env=True)
    print(document.pformat())
    assert "\n".join(
        [ll.rstrip() for ll in document.pformat().splitlines()]
    ) == "\n".join([ll.rstrip() for ll in expected.splitlines()])


@pytest.mark.parametrize(
    "line,title,input,expected",
    read_fixture_file(FIXTURE_PATH.joinpath("definition_lists.md")),
    ids=[
        f"{i[0]}-{i[1]}"
        for i in read_fixture_file(FIXTURE_PATH / "definition_lists.md")
    ],
)
def test_definition_lists(line, title, input, expected):
    document = to_docutils(
        input, MdParserConfig(enable_extensions=["deflist"]), in_sphinx_env=True
    )
    print(document.pformat())
    assert "\n".join(
        [ll.rstrip() for ll in document.pformat().splitlines()]
    ) == "\n".join([ll.rstrip() for ll in expected.splitlines()])
