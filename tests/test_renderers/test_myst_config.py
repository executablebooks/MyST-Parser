"""Test (docutils) parsing with different ``MdParserConfig`` options set."""

import shlex
from io import StringIO
from pathlib import Path

import pytest
from docutils import __version_info__ as docutils_version
from docutils.core import Publisher, publish_string
from pytest_param_files import ParamTestData

from myst_parser.parsers.docutils_ import Parser

FIXTURE_PATH = Path(__file__).parent.joinpath("fixtures")
INV_PATH = Path(__file__).parent.parent.absolute() / "static" / "objects_v2.inv"


@pytest.mark.param_file(FIXTURE_PATH / "myst-config.txt")
def test_cmdline(file_params: ParamTestData, normalize_doctree_xml):
    """The description is parsed as a docutils commandline"""
    if file_params.title == "attrs_image" and docutils_version < (0, 22):
        # loose system messages are also output to ast in 0.22 https://github.com/live-clones/docutils/commit/dc4e16315b4fbe391417a6f7aad215b9389a9c74
        pytest.skip("different in docutils>=0.22")
    pub = Publisher(parser=Parser())
    try:
        pub.process_command_line(shlex.split(file_params.description or ""))
    except Exception as err:
        raise AssertionError(
            f"Failed to parse commandline: {file_params.description}\n{err}"
        ) from err
    settings = vars(pub.settings)
    report_stream = StringIO()
    settings["output_encoding"] = "unicode"
    settings["warning_stream"] = report_stream
    if "inv_" in file_params.title:
        settings["myst_inventories"] = {"key": ["https://example.com", str(INV_PATH)]}
    output = publish_string(
        file_params.content,
        parser=Parser(),
        writer_name="pseudoxml",
        settings_overrides=settings,
    )
    output = normalize_doctree_xml(output)
    warnings = report_stream.getvalue()
    if warnings:
        output += "\n" + warnings
    file_params.assert_expected(output, rstrip_lines=True)
