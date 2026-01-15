"""Tests of the warning reporting for different MyST Markdown inputs."""

from io import StringIO
from pathlib import Path

import pytest
from docutils.core import publish_doctree

from myst_parser.parsers.docutils_ import Parser

FIXTURE_PATH = Path(__file__).parent.joinpath("fixtures")


@pytest.mark.param_file(FIXTURE_PATH / "reporter_warnings.md")
def test_basic(file_params):
    """Test basic functionality."""
    report_stream = StringIO()
    publish_doctree(
        file_params.content,
        parser=Parser(),
        settings_overrides={"warning_stream": report_stream},
    )
    text = report_stream.getvalue()
    # changed in docutils 0.23
    text = text.replace(
        "corresponding footnote available", "corresponding footnotes available"
    )
    file_params.assert_expected(text, rstrip=True)
