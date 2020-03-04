"""In this module tests are run against the full test set,
provided by https://github.com/commonmark/CommonMark.git.
"""
import json
import os

import pytest

from myst_parser.block_tokens import Document
from myst_parser.html_renderer import HTMLRenderer

with open(os.path.join(os.path.dirname(__file__), "commonmark.json"), "r") as fin:
    tests = json.load(fin)


@pytest.mark.parametrize("entry", tests)
def test_commonmark(entry):
    if entry["example"] in [65, 67]:
        # This is supported by numerous Markdown flavours, but not strictly CommonMark
        # see: https://talk.commonmark.org/t/metadata-in-documents/721/86
        pytest.skip(
            "Thematic breaks on the first line conflict with front matter syntax"
        )
    test_case = entry["markdown"].splitlines(keepends=True)
    with HTMLRenderer() as renderer:
        output = renderer.render(Document(test_case))
    assert output == entry["html"]
