from io import StringIO
from pathlib import Path

import pytest
from docutils.core import publish_doctree
from markdown_it.utils import read_fixture_file

from myst_parser.docutils_ import Parser

FIXTURE_PATH = Path(__file__).parent.joinpath("fixtures")


@pytest.mark.parametrize(
    "line,title,input,expected",
    read_fixture_file(FIXTURE_PATH.joinpath("reporter_warnings.md")),
    ids=[
        f"{i[0]}-{i[1]}"
        for i in read_fixture_file(FIXTURE_PATH / "reporter_warnings.md")
    ],
)
def test_basic(line, title, input, expected):
    """Test basic functionality."""
    report_stream = StringIO()
    publish_doctree(
        input, parser=Parser(), settings_overrides={"warning_stream": report_stream}
    )

    assert report_stream.getvalue().rstrip() == expected.rstrip()
