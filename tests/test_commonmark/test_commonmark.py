"""In this module tests are run against the full test set,
provided by https://github.com/commonmark/CommonMark.git.
"""
import json
import os

import pytest
from markdown_it.renderer import RendererHTML

from myst_parser.config.main import MdParserConfig
from myst_parser.parsers.mdit import create_md_parser

with open(
    os.path.join(os.path.dirname(__file__), "commonmark.json"), encoding="utf8"
) as fin:
    tests = json.load(fin)


@pytest.mark.parametrize("entry", tests)
def test_commonmark(entry):
    if entry["example"] == 14:
        # This is just a test that +++ are not parsed as thematic breaks
        pytest.skip("Expects '+++' to be unconverted (not block break).")
    if entry["example"] in [66, 68]:
        # Front matter is supported by numerous Markdown flavours,
        # but not strictly CommonMark,
        # see: https://talk.commonmark.org/t/metadata-in-documents/721/86
        pytest.skip(
            "Thematic breaks on the first line conflict with front matter syntax"
        )
    test_case = entry["markdown"]
    md = create_md_parser(MdParserConfig(), RendererHTML)
    output = md.render(test_case)

    if entry["example"] == 593:
        # this doesn't have any bearing on the output
        output = output.replace("mailto", "MAILTO")
    if entry["example"] in [187, 209, 210]:
        # this doesn't have any bearing on the output
        output = output.replace(
            "<blockquote></blockquote>", "<blockquote>\n</blockquote>"
        )

    assert output == entry["html"]
