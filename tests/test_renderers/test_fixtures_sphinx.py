"""Test fixture files, using the ``SphinxRenderer``.

Note, the output AST is before any transforms are applied.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest
from sphinx_pytest.plugin import CreateDoctree

from myst_parser.mdit_to_docutils.sphinx_ import SphinxRenderer

FIXTURE_PATH = Path(__file__).parent.joinpath("fixtures")


@pytest.mark.param_file(FIXTURE_PATH / "sphinx_syntax_elements.md")
def test_syntax_elements(file_params, sphinx_doctree_no_tr: CreateDoctree):
    sphinx_doctree_no_tr.set_conf({"extensions": ["myst_parser"]})
    result = sphinx_doctree_no_tr(file_params.content, "index.md")
    file_params.assert_expected(result.pformat("index"), rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "sphinx_link_resolution.md")
def test_link_resolution(file_params, sphinx_doctree: CreateDoctree):
    sphinx_doctree.set_conf(
        {"extensions": ["myst_parser"], **settings_from_json(file_params.description)}
    )
    sphinx_doctree.srcdir.joinpath("test.txt").touch()
    sphinx_doctree.srcdir.joinpath("other.rst").write_text(":orphan:\n\nTest\n====")
    result = sphinx_doctree(file_params.content, "index.md")
    outcome = result.pformat("index")
    if result.warnings.strip():
        outcome += "\n\n" + result.warnings.strip()
    file_params.assert_expected(outcome, rstrip_lines=True)


def settings_from_json(string: str | None):
    """Parse the description for a JSON settings string."""
    if string is None or not string.strip():
        return {}
    try:
        data = json.loads(string)
        assert isinstance(data, dict), "settings must be a JSON object"
    except Exception as err:
        raise AssertionError(f"Failed to parse JSON settings: {string}\n{err}")
    return data


@pytest.mark.param_file(FIXTURE_PATH / "tables.md")
def test_tables(file_params, sphinx_doctree_no_tr: CreateDoctree):
    sphinx_doctree_no_tr.set_conf({"extensions": ["myst_parser"]})
    result = sphinx_doctree_no_tr(file_params.content, "index.md")
    file_params.assert_expected(result.pformat("index"), rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "directive_options.md")
def test_directive_options(file_params, sphinx_doctree_no_tr: CreateDoctree):
    sphinx_doctree_no_tr.set_conf({"extensions": ["myst_parser"]})
    result = sphinx_doctree_no_tr(file_params.content, "index.md")
    file_params.assert_expected(result.pformat("index"), rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "sphinx_directives.md")
def test_sphinx_directives(file_params, sphinx_doctree_no_tr: CreateDoctree):
    # TODO fix skipped directives
    # TODO test domain directives
    if file_params.title.startswith("SKIP") or file_params.title.startswith(
        "SPHINX4-SKIP"
    ):
        pytest.skip(file_params.title)

    sphinx_doctree_no_tr.set_conf({"extensions": ["myst_parser"]})
    pformat = sphinx_doctree_no_tr(file_params.content, "index.md").pformat("index")
    # see https://github.com/sphinx-doc/sphinx/issues/9827
    pformat = pformat.replace('<glossary sorted="False">', "<glossary>")
    # see https://github.com/executablebooks/MyST-Parser/issues/522
    if sys.maxsize == 2147483647:
        pformat = pformat.replace('"2147483647"', '"9223372036854775807"')
    # changed in sphinx 5.3 for desc node
    pformat = pformat.replace('nocontentsentry="False" ', "")
    pformat = pformat.replace('noindexentry="False" ', "")
    # changed in sphinx 5.3 for desc_signature node
    pformat = pformat.replace('_toc_name="" _toc_parts="()" ', "")
    pformat = pformat.replace('_toc_name=".. a::" _toc_parts="(\'a\',)" ', "")
    pformat = pformat.replace('fullname="a" ', "")
    file_params.assert_expected(pformat, rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "sphinx_roles.md")
def test_sphinx_roles(file_params, sphinx_doctree_no_tr: CreateDoctree):
    if file_params.title.startswith("SKIP"):
        pytest.skip(file_params.title)

    sphinx_doctree_no_tr.set_conf({"extensions": ["myst_parser"]})
    pformat = sphinx_doctree_no_tr(file_params.content, "index.md").pformat("index")
    # sphinx 3 adds a parent key
    pformat = re.sub('cpp:parent_key="[^"]*"', 'cpp:parent_key=""', pformat)
    # sphinx >= 4.5.0 adds a trailing slash to PEP URLs,
    # see https://github.com/sphinx-doc/sphinx/commit/658689433eacc9eb
    pformat = pformat.replace(
        ' refuri="http://www.python.org/dev/peps/pep-0001">',
        ' refuri="http://www.python.org/dev/peps/pep-0001/">',
    )
    file_params.assert_expected(pformat, rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "dollarmath.md")
def test_dollarmath(file_params, sphinx_doctree_no_tr: CreateDoctree):
    sphinx_doctree_no_tr.set_conf(
        {"extensions": ["myst_parser"], "myst_enable_extensions": ["dollarmath"]}
    )
    result = sphinx_doctree_no_tr(file_params.content, "index.md")
    file_params.assert_expected(result.pformat("index"), rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "amsmath.md")
def test_amsmath(file_params, sphinx_doctree_no_tr: CreateDoctree, monkeypatch):
    monkeypatch.setattr(SphinxRenderer, "_random_label", lambda self: "mock-uuid")
    sphinx_doctree_no_tr.set_conf(
        {"extensions": ["myst_parser"], "myst_enable_extensions": ["amsmath"]}
    )
    result = sphinx_doctree_no_tr(file_params.content, "index.md")
    file_params.assert_expected(result.pformat("index"), rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "containers.md")
def test_containers(file_params, sphinx_doctree_no_tr: CreateDoctree, monkeypatch):
    monkeypatch.setattr(SphinxRenderer, "_random_label", lambda self: "mock-uuid")
    sphinx_doctree_no_tr.set_conf(
        {"extensions": ["myst_parser"], "myst_enable_extensions": ["colon_fence"]}
    )
    result = sphinx_doctree_no_tr(file_params.content, "index.md")
    file_params.assert_expected(result.pformat("index"), rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "eval_rst.md")
def test_evalrst_elements(file_params, sphinx_doctree_no_tr: CreateDoctree):
    sphinx_doctree_no_tr.set_conf({"extensions": ["myst_parser"]})
    result = sphinx_doctree_no_tr(file_params.content, "index.md")
    file_params.assert_expected(result.pformat("index"), rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "definition_lists.md")
def test_definition_lists(file_params, sphinx_doctree_no_tr: CreateDoctree):
    sphinx_doctree_no_tr.set_conf(
        {"extensions": ["myst_parser"], "myst_enable_extensions": ["deflist"]}
    )
    result = sphinx_doctree_no_tr(file_params.content, "index.md")
    file_params.assert_expected(result.pformat("index"), rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "attributes.md")
def test_attributes(file_params, sphinx_doctree_no_tr: CreateDoctree):
    sphinx_doctree_no_tr.set_conf(
        {
            "extensions": ["myst_parser"],
            "myst_enable_extensions": ["attrs_inline", "attrs_block"],
        }
    )
    result = sphinx_doctree_no_tr(file_params.content, "index.md")
    file_params.assert_expected(result.pformat("index"), rstrip_lines=True)
