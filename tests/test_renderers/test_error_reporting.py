"""Tests of the warning reporting for different MyST Markdown inputs."""

import re
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


@pytest.mark.parametrize("preamble", ["", "```{note}\nA note.\n```\n"])
def test_eval_rst_include_locations(tmp_path, preamble):
    """An ``.. include::`` in ``{eval-rst}`` must not shift later warning locations."""
    included = tmp_path / "inc.rst"
    included.write_text("Line 1.\n\nAn *unclosed on line 3.\n", encoding="utf8")
    content = preamble + (
        "```{eval-rst}\n"
        f".. include:: {included.as_posix()}\n"
        "\n"
        "Block 1 *unclosed.\n"
        "```\n"
        "\n"
        "```{eval-rst}\n"
        "Block 2 *unclosed.\n"
        "```\n"
        "\n"
        "{unknown-role}`x`\n"
    )
    offset = preamble.count("\n")
    report_stream = StringIO()
    publish_doctree(
        content,
        source_path=str(tmp_path / "index.md"),
        parser=Parser(),
        settings_overrides={"warning_stream": report_stream},
    )
    locations = [
        (Path(source).name, int(line))
        for source, line in re.findall(
            r"^(.+?):(\d+): \(", report_stream.getvalue(), re.MULTILINE
        )
    ]
    assert set(locations) == {
        ("inc.rst", 3),
        ("index.md", offset + 4),
        ("index.md", offset + 8),
        ("index.md", offset + 11),
    }
