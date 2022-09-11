"""Tests of the warning reporting for different MyST Markdown inputs."""
from io import StringIO
from pathlib import Path

import pytest
from docutils.core import publish_doctree

from myst_parser.parsers.docutils_ import Parser

FIXTURE_PATH = Path(__file__).parent.joinpath("fixtures")


@pytest.mark.param_file(FIXTURE_PATH / "warnings_docutils.md")
def test_basic(file_params):
    """Test basic functionality."""
    report_stream = StringIO()
    settings_overrides = {"warning_stream": report_stream}
    if "[ANCHORS]" in file_params.title:
        settings_overrides["myst_heading_anchors"] = 2
    publish_doctree(
        file_params.content,
        parser=Parser(),
        settings_overrides=settings_overrides,
    )
    file_params.assert_expected(report_stream.getvalue(), rstrip=True)
