"""Test fixture files, using the ``SphinxRenderer``.

Note, the output AST is before any transforms are applied.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest
from docutils.core import Publisher
from pytest_param_files import ParamTestData
from sphinx.transforms import SphinxTransformer
from sphinx_pytest.plugin import CreateDoctree

from myst_parser.mdit_to_docutils.sphinx_ import SphinxRenderer

FIXTURE_PATH = Path(__file__).parent.joinpath("fixtures")


@pytest.mark.param_file(FIXTURE_PATH / "sphinx_syntax_elements.md")
def test_syntax_elements(
    file_params: ParamTestData,
    sphinx_doctree: CreateDoctree,
    monkeypatch,
    normalize_doctree_xml,
):
    sphinx_doctree.set_conf({"extensions": ["myst_parser"], "show_warning_types": True})

    def _apply_transforms(self):
        pass

    if "[APPLY TRANSFORMS]" not in file_params.title:
        monkeypatch.setattr(Publisher, "apply_transforms", _apply_transforms)
        # in sphinx >= 9.0.0 SphinxTransformer is used
        monkeypatch.setattr(SphinxTransformer, "apply_transforms", _apply_transforms)

    result = sphinx_doctree(file_params.content, "index.md")
    pformat = normalize_doctree_xml(result.pformat("index"))
    replacements = {
        # changed in docutils 0.20.1
        '<literal classes="code" language="">': '<literal classes="code">',
        # changed in sphinx 9
        '<image alt="" uri="">': '<image alt="" candidates="{\'*\': \'.\'}" original_uri="" uri=".">',
        '<image alt="alt" title="title" uri="src">': '<image alt="alt" candidates="{\'*\': \'src\'}" title="title" uri="src">',
        '<image alt="alt" uri="http://www.google%3C%3E.com">': '<image alt="alt" candidates="{\'?\': \'http://www.google%3C%3E.com\'}" uri="http://www.google%3C%3E.com">',
    }
    for old, new in replacements.items():
        pformat = pformat.replace(old, new)
    file_params.assert_expected(pformat, rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "sphinx_link_resolution.md")
def test_link_resolution(
    file_params: ParamTestData, sphinx_doctree: CreateDoctree, normalize_doctree_xml
):
    sphinx_doctree.set_conf(
        {"extensions": ["myst_parser"], **settings_from_json(file_params.description)}
    )
    sphinx_doctree.srcdir.joinpath("test.txt").touch()
    sphinx_doctree.srcdir.joinpath("other.rst").write_text(":orphan:\n\nTest\n====")
    result = sphinx_doctree(file_params.content, "index.md")
    outcome = normalize_doctree_xml(result.pformat("index"))
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
        raise AssertionError(f"Failed to parse JSON settings: {string}\n{err}") from err
    return data


@pytest.mark.param_file(FIXTURE_PATH / "tables.md")
def test_tables(
    file_params: ParamTestData,
    sphinx_doctree_no_tr: CreateDoctree,
    normalize_doctree_xml,
):
    sphinx_doctree_no_tr.set_conf({"extensions": ["myst_parser"]})
    result = sphinx_doctree_no_tr(file_params.content, "index.md")
    file_params.assert_expected(
        normalize_doctree_xml(result.pformat("index")), rstrip_lines=True
    )


@pytest.mark.param_file(FIXTURE_PATH / "directive_options.md")
def test_directive_options(
    file_params: ParamTestData,
    sphinx_doctree_no_tr: CreateDoctree,
    normalize_doctree_xml,
):
    sphinx_doctree_no_tr.set_conf({"extensions": ["myst_parser"]})
    result = sphinx_doctree_no_tr(file_params.content, "index.md")
    file_params.assert_expected(
        normalize_doctree_xml(result.pformat("index")), rstrip_lines=True
    )


@pytest.mark.param_file(FIXTURE_PATH / "sphinx_directives.md")
def test_sphinx_directives(
    file_params: ParamTestData,
    sphinx_doctree_no_tr: CreateDoctree,
    normalize_doctree_xml,
):
    # TODO fix skipped directives
    # TODO test domain directives
    if file_params.title.startswith("SKIP"):
        pytest.skip(file_params.title)

    sphinx_doctree_no_tr.set_conf({"extensions": ["myst_parser"]})
    pformat = normalize_doctree_xml(
        sphinx_doctree_no_tr(file_params.content, "index.md").pformat("index")
    )
    # see https://github.com/executablebooks/MyST-Parser/issues/522
    if sys.maxsize == 2147483647:
        pformat = pformat.replace('"2147483647"', '"9223372036854775807"')
    file_params.assert_expected(pformat, rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "sphinx_roles.md")
def test_sphinx_roles(
    file_params: ParamTestData,
    sphinx_doctree_no_tr: CreateDoctree,
    normalize_doctree_xml,
):
    if file_params.title.startswith("SKIP"):
        pytest.skip(file_params.title)

    sphinx_doctree_no_tr.set_conf({"extensions": ["myst_parser"]})
    pformat = normalize_doctree_xml(
        sphinx_doctree_no_tr(file_params.content, "index.md").pformat("index")
    )
    # sphinx 3 adds a parent key
    pformat = re.sub('cpp:parent_key="[^"]*"', 'cpp:parent_key=""', pformat)
    # sphinx >= 4.5.0 adds a trailing slash to PEP URLs,
    # see https://github.com/sphinx-doc/sphinx/commit/658689433eacc9eb
    pformat = pformat.replace(
        ' refuri="http://www.python.org/dev/peps/pep-0001">',
        ' refuri="http://www.python.org/dev/peps/pep-0001/">',
    )
    if file_params.title == "js:class (`sphinx.domains.javascript.JSConstructor`):":
        # sphinx 9 change
        pformat = pformat.replace("a()", "a")
    file_params.assert_expected(pformat, rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "dollarmath.md")
def test_dollarmath(
    file_params: ParamTestData,
    sphinx_doctree_no_tr: CreateDoctree,
    normalize_doctree_xml,
):
    sphinx_doctree_no_tr.set_conf(
        {"extensions": ["myst_parser"], "myst_enable_extensions": ["dollarmath"]}
    )
    result = sphinx_doctree_no_tr(file_params.content, "index.md")
    file_params.assert_expected(
        normalize_doctree_xml(result.pformat("index")), rstrip_lines=True
    )


@pytest.mark.param_file(FIXTURE_PATH / "amsmath.md")
def test_amsmath(
    file_params: ParamTestData,
    sphinx_doctree_no_tr: CreateDoctree,
    monkeypatch,
    normalize_doctree_xml,
):
    monkeypatch.setattr(SphinxRenderer, "_random_label", lambda self: "mock-uuid")
    sphinx_doctree_no_tr.set_conf(
        {"extensions": ["myst_parser"], "myst_enable_extensions": ["amsmath"]}
    )
    result = sphinx_doctree_no_tr(file_params.content, "index.md")
    file_params.assert_expected(
        normalize_doctree_xml(result.pformat("index")), rstrip_lines=True
    )


@pytest.mark.param_file(FIXTURE_PATH / "containers.md")
def test_containers(
    file_params: ParamTestData,
    sphinx_doctree_no_tr: CreateDoctree,
    monkeypatch,
    normalize_doctree_xml,
):
    monkeypatch.setattr(SphinxRenderer, "_random_label", lambda self: "mock-uuid")
    sphinx_doctree_no_tr.set_conf(
        {"extensions": ["myst_parser"], "myst_enable_extensions": ["colon_fence"]}
    )
    result = sphinx_doctree_no_tr(file_params.content, "index.md")
    file_params.assert_expected(
        normalize_doctree_xml(result.pformat("index")), rstrip_lines=True
    )


@pytest.mark.param_file(FIXTURE_PATH / "eval_rst.md")
def test_evalrst_elements(
    file_params: ParamTestData,
    sphinx_doctree_no_tr: CreateDoctree,
    normalize_doctree_xml,
):
    sphinx_doctree_no_tr.set_conf({"extensions": ["myst_parser"]})
    result = sphinx_doctree_no_tr(file_params.content, "index.md")
    file_params.assert_expected(
        normalize_doctree_xml(result.pformat("index")), rstrip_lines=True
    )


@pytest.mark.param_file(FIXTURE_PATH / "definition_lists.md")
def test_definition_lists(
    file_params: ParamTestData,
    sphinx_doctree_no_tr: CreateDoctree,
    normalize_doctree_xml,
):
    sphinx_doctree_no_tr.set_conf(
        {"extensions": ["myst_parser"], "myst_enable_extensions": ["deflist"]}
    )
    result = sphinx_doctree_no_tr(file_params.content, "index.md")
    file_params.assert_expected(
        normalize_doctree_xml(result.pformat("index")), rstrip_lines=True
    )


@pytest.mark.param_file(FIXTURE_PATH / "attributes.md")
def test_attributes(
    file_params: ParamTestData,
    sphinx_doctree_no_tr: CreateDoctree,
    normalize_doctree_xml,
):
    sphinx_doctree_no_tr.set_conf(
        {
            "extensions": ["myst_parser"],
            "myst_enable_extensions": ["attrs_inline", "attrs_block"],
        }
    )
    result = sphinx_doctree_no_tr(file_params.content, "index.md")
    file_params.assert_expected(
        normalize_doctree_xml(result.pformat("index")), rstrip_lines=True
    )
