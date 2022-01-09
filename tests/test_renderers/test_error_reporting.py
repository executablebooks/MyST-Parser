"""Tests of the warning reporting for different MyST Markdown inputs."""
from io import StringIO
from pathlib import Path

from docutils.core import publish_doctree
from pytest_param_files import with_parameters

from myst_parser.docutils_ import Parser

FIXTURE_PATH = Path(__file__).parent.joinpath("fixtures")


@with_parameters(FIXTURE_PATH / "reporter_warnings.md")
def test_basic(file_params):
    """Test basic functionality."""
    report_stream = StringIO()
    publish_doctree(
        file_params.content,
        parser=Parser(),
        settings_overrides={"warning_stream": report_stream},
    )
    file_params.assert_expected(report_stream.getvalue(), rstrip=True)
