"""Test fixture files, using the ``DocutilsRenderer``.

Note, the output AST is before any transforms are applied.
"""

from __future__ import annotations

import shlex
from io import StringIO
from pathlib import Path
from typing import Any

import pytest
from tests.conftest import normalize_doctree_xml
from docutils import __version_info__ as docutils_version
from docutils.core import Publisher, publish_doctree
from pytest_param_files import ParamTestData

from myst_parser.parsers.docutils_ import Parser

FIXTURE_PATH = Path(__file__).parent.joinpath("fixtures")


@pytest.mark.param_file(FIXTURE_PATH / "docutil_syntax_elements.md")
def test_syntax_elements(file_params: ParamTestData, monkeypatch):
    """Test conversion of Markdown to docutils AST (before transforms are applied)."""

    def _apply_transforms(self):
        pass

    if "[APPLY TRANSFORMS]" not in file_params.title:
        monkeypatch.setattr(Publisher, "apply_transforms", _apply_transforms)

    doctree = publish_doctree(
        file_params.content,
        source_path="notset",
        parser=Parser(),
        settings_overrides={"myst_highlight_code_blocks": False},
    )

    # in docutils 0.18 footnote ids have changed
    outcome = normalize_doctree_xml(doctree.pformat()).replace(
        '"footnote-reference-1"', '"id1"'
    )
    outcome = outcome.replace(' language=""', "")
    file_params.assert_expected(outcome, rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "docutil_link_resolution.md")
def test_link_resolution(file_params: ParamTestData):
    """Test that Markdown links resolve to the correct target, or give the correct warning."""
    settings = settings_from_cmdline(file_params.description)
    report_stream = StringIO()
    settings["warning_stream"] = report_stream
    if file_params.title == "explicit>implicit":
        if docutils_version < (0, 22):
            # reporting changed in docutils 0.22
            pytest.skip("different in docutils>=0.22")
        settings["report_level"] = 0
    doctree = publish_doctree(
        file_params.content,
        source_path="<src>/index.md",
        parser=Parser(),
        settings_overrides=settings,
    )
    outcome = normalize_doctree_xml(doctree.pformat())
    if report_stream.getvalue().strip():
        outcome += "\n\n" + report_stream.getvalue().strip()
    file_params.assert_expected(outcome, rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "docutil_roles.md")
def test_docutils_roles(file_params: ParamTestData, monkeypatch):
    """Test conversion of Markdown to docutils AST (before transforms are applied)."""

    def _apply_transforms(self):
        pass

    monkeypatch.setattr(Publisher, "apply_transforms", _apply_transforms)

    doctree = publish_doctree(
        file_params.content,
        source_path="notset",
        parser=Parser(),
    )

    file_params.assert_expected(
        normalize_doctree_xml(doctree.pformat()), rstrip_lines=True
    )


@pytest.mark.param_file(FIXTURE_PATH / "docutil_directives.md")
def test_docutils_directives(file_params: ParamTestData, monkeypatch):
    """Test output of docutils directives."""
    if "SKIP" in file_params.description:  # line-block directive not yet supported
        pytest.skip(file_params.description)

    def _apply_transforms(self):
        pass

    monkeypatch.setattr(Publisher, "apply_transforms", _apply_transforms)

    doctree = publish_doctree(
        file_params.content,
        source_path="notset",
        parser=Parser(),
    )

    file_params.assert_expected(
        normalize_doctree_xml(doctree.pformat()), rstrip_lines=True
    )


@pytest.mark.param_file(FIXTURE_PATH / "docutil_syntax_extensions.txt")
def test_syntax_extensions(file_params: ParamTestData):
    """The description is parsed as a docutils commandline"""
    settings = settings_from_cmdline(file_params.description)
    report_stream = StringIO()
    settings["warning_stream"] = report_stream
    doctree = publish_doctree(
        file_params.content,
        parser=Parser(),
        settings_overrides=settings,
    )
    file_params.assert_expected(
        normalize_doctree_xml(doctree.pformat()), rstrip_lines=True
    )


def settings_from_cmdline(cmdline: str | None) -> dict[str, Any]:
    """Parse a docutils commandline into a settings dictionary"""
    if cmdline is None or not cmdline.strip():
        return {}
    pub = Publisher(parser=Parser())
    try:
        pub.process_command_line(shlex.split(cmdline))
    except Exception as err:
        raise AssertionError(f"Failed to parse commandline: {cmdline}\n{err}") from err
    return vars(pub.settings)
