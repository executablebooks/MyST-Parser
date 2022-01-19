"""Test fixture files, using the ``SphinxRenderer``.

Note, the output AST is before any transforms are applied.
"""
import re
from pathlib import Path

import pytest
import sphinx

from myst_parser.main import MdParserConfig, to_docutils
from myst_parser.sphinx_renderer import SphinxRenderer, mock_sphinx_env

FIXTURE_PATH = Path(__file__).parent.joinpath("fixtures")


def test_minimal_sphinx():
    with mock_sphinx_env(conf={"author": "bob geldof"}, with_builder=True) as app:
        assert app.config["author"] == "bob geldof"


@pytest.mark.param_file(FIXTURE_PATH / "sphinx_syntax_elements.md")
def test_syntax_elements(file_params):
    document = to_docutils(file_params.content, in_sphinx_env=True)
    file_params.assert_expected(document.pformat(), rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "tables.md")
def test_tables(file_params):
    document = to_docutils(file_params.content, in_sphinx_env=True)
    file_params.assert_expected(document.pformat(), rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "directive_options.md")
def test_directive_options(file_params):
    document = to_docutils(file_params.content)
    file_params.assert_expected(document.pformat(), rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "sphinx_directives.md")
def test_sphinx_directives(file_params):
    # TODO fix skipped directives
    # TODO test domain directives
    if file_params.title.startswith("SKIP"):
        pytest.skip(file_params.title)
    elif file_params.title.startswith("SPHINX3") and sphinx.version_info[0] < 3:
        pytest.skip(file_params.title)
    elif file_params.title.startswith("SPHINX4") and sphinx.version_info[0] < 4:
        pytest.skip(file_params.title)
    document = to_docutils(file_params.content, in_sphinx_env=True)
    file_params.assert_expected(document.pformat(), rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "sphinx_roles.md")
def test_sphinx_roles(file_params):
    if file_params.title.startswith("SKIP"):
        pytest.skip(file_params.title)
    elif file_params.title.startswith("SPHINX4") and sphinx.version_info[0] < 4:
        pytest.skip(file_params.title)
    document = to_docutils(file_params.content, in_sphinx_env=True)
    actual = document.pformat()
    # sphinx 3 adds a parent key
    actual = re.sub('cpp:parent_key="[^"]*"', 'cpp:parent_key=""', actual)
    file_params.assert_expected(actual, rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "dollarmath.md")
def test_dollarmath(file_params, monkeypatch):
    document = to_docutils(
        file_params.content,
        MdParserConfig(enable_extensions=["dollarmath"]),
        in_sphinx_env=True,
    )
    file_params.assert_expected(document.pformat(), rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "amsmath.md")
def test_amsmath(file_params, monkeypatch):
    monkeypatch.setattr(SphinxRenderer, "_random_label", lambda self: "mock-uuid")
    document = to_docutils(
        file_params.content,
        MdParserConfig(enable_extensions=["amsmath"]),
        in_sphinx_env=True,
    )
    file_params.assert_expected(document.pformat(), rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "containers.md")
def test_containers(file_params, monkeypatch):
    monkeypatch.setattr(SphinxRenderer, "_random_label", lambda self: "mock-uuid")
    document = to_docutils(
        file_params.content,
        MdParserConfig(enable_extensions=["colon_fence"]),
        in_sphinx_env=True,
    )
    file_params.assert_expected(document.pformat(), rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "eval_rst.md")
def test_evalrst_elements(file_params):
    document = to_docutils(file_params.content, in_sphinx_env=True)
    file_params.assert_expected(document.pformat(), rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "definition_lists.md")
def test_definition_lists(file_params):
    document = to_docutils(
        file_params.content,
        MdParserConfig(enable_extensions=["deflist"]),
        in_sphinx_env=True,
    )
    file_params.assert_expected(document.pformat(), rstrip_lines=True)
