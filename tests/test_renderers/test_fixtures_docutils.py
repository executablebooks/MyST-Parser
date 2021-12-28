"""Test fixture files, using the ``DocutilsRenderer``.

Note, the output AST is before any transforms are applied.
"""
from pathlib import Path

import pytest
from markdown_it.utils import read_fixture_file

from myst_parser.docutils_renderer import DocutilsRenderer, make_document
from myst_parser.main import MdParserConfig, create_md_parser

FIXTURE_PATH = Path(__file__).parent.joinpath("fixtures")


@pytest.mark.parametrize(
    "line,title,input,expected",
    read_fixture_file(FIXTURE_PATH.joinpath("docutil_roles.md")),
    ids=[
        f"{i[0]}-{i[1]}" for i in read_fixture_file(FIXTURE_PATH / "docutil_roles.md")
    ],
)
def test_docutils_roles(line, title, input, expected):
    """Test output of docutils roles."""
    parser = create_md_parser(MdParserConfig(), DocutilsRenderer)
    parser.options["document"] = document = make_document()
    parser.render(input)
    try:
        assert "\n".join(
            [ll.rstrip() for ll in document.pformat().splitlines()]
        ) == "\n".join([ll.rstrip() for ll in expected.splitlines()])
    except AssertionError:
        print(document.pformat())
        raise


@pytest.mark.parametrize(
    "line,title,input,expected",
    read_fixture_file(FIXTURE_PATH.joinpath("docutil_directives.md")),
    ids=[
        f"{i[0]}-{i[1]}"
        for i in read_fixture_file(FIXTURE_PATH / "docutil_directives.md")
    ],
)
def test_docutils_directives(line, title, input, expected):
    """Test output of docutils directives."""
    if title.startswith("SKIP"):  # line-block directive not yet supported
        pytest.skip(title)
    parser = create_md_parser(MdParserConfig(), DocutilsRenderer)
    parser.options["document"] = document = make_document()
    parser.render(input)
    try:
        assert "\n".join(
            [ll.rstrip() for ll in document.pformat().splitlines()]
        ) == "\n".join([ll.rstrip() for ll in expected.splitlines()])
    except AssertionError:
        print(document.pformat())
        raise
