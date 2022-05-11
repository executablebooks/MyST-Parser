"""Test (docutils) parsing with different ``MdParserConfig`` options set."""
import shlex
from io import StringIO
from pathlib import Path

import pytest
from docutils.core import Publisher, publish_doctree

from myst_parser.parsers.docutils_ import Parser

FIXTURE_PATH = Path(__file__).parent.joinpath("fixtures")


@pytest.mark.param_file(FIXTURE_PATH / "myst-config.txt")
def test_cmdline(file_params):
    """The description is parsed as a docutils commandline"""
    pub = Publisher(parser=Parser())
    option_parser = pub.setup_option_parser()
    try:
        settings = option_parser.parse_args(
            shlex.split(file_params.description)
        ).__dict__
    except Exception as err:
        raise AssertionError(
            f"Failed to parse commandline: {file_params.description}\n{err}"
        )
    report_stream = StringIO()
    settings["warning_stream"] = report_stream
    doctree = publish_doctree(
        file_params.content,
        parser=Parser(),
        settings_overrides=settings,
    )
    file_params.assert_expected(doctree.pformat(), rstrip_lines=True)
