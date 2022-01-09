"""Test fixture files, using the ``DocutilsRenderer``.

Note, the output AST is before any transforms are applied.
"""
from pathlib import Path

import pytest

from myst_parser.docutils_renderer import DocutilsRenderer, make_document
from myst_parser.main import MdParserConfig, create_md_parser

FIXTURE_PATH = Path(__file__).parent.joinpath("fixtures")


@pytest.mark.param_file(FIXTURE_PATH / "docutil_syntax_elements.md")
def test_syntax_elements(file_params):
    parser = create_md_parser(
        MdParserConfig(highlight_code_blocks=False), DocutilsRenderer
    )
    parser.options["document"] = document = make_document()
    parser.render(file_params.content)
    # in docutils 0.18 footnote ids have changed
    outcome = document.pformat().replace('"footnote-reference-1"', '"id1"')
    file_params.assert_expected(outcome, rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "docutil_roles.md")
def test_docutils_roles(file_params):
    """Test output of docutils roles."""
    parser = create_md_parser(MdParserConfig(), DocutilsRenderer)
    parser.options["document"] = document = make_document()
    parser.render(file_params.content)
    file_params.assert_expected(document.pformat(), rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "docutil_directives.md")
def test_docutils_directives(file_params):
    """Test output of docutils directives."""
    if "SKIP" in file_params.description:  # line-block directive not yet supported
        pytest.skip(file_params.description)
    parser = create_md_parser(MdParserConfig(), DocutilsRenderer)
    parser.options["document"] = document = make_document()
    parser.render(file_params.content)
    file_params.assert_expected(document.pformat(), rstrip_lines=True)
