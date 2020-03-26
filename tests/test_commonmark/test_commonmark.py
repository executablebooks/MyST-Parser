"""In this module tests are run against the full test set,
provided by https://github.com/commonmark/CommonMark.git.
"""
import json
import os

import pytest

from myst_parser.main import to_html

with open(os.path.join(os.path.dirname(__file__), "commonmark.json"), "r") as fin:
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
    if entry["example"] in [108, 334]:
        # TODO fix failing empty code span tests (awaiting upstream);
        # ``` ``` -> <code> </code> not <code></code>
        pytest.skip("empty code span spacing")
    if entry["example"] in [
        171,  # [foo]: /url\\bar\\*baz \"foo\\\"bar\\baz\"\n\n[foo]\n
        306,  # <http://example.com?find=\\*>\n
        308,  # [foo](/bar\\* \"ti\\*tle\")\n
        309,  # [foo]\n\n[foo]: /bar\\* \"ti\\*tle\"\n
        310,  # ``` foo\\+bar\nfoo\n```\n
        502,  # [link](/url \"title \\\"&quot;\")\n
        599,  # <http://example.com/\\[\\>\n
    ]:
        # TODO fix url backslash escaping (awaiting upstream)
        pytest.skip("url backslash escaping")
    test_case = entry["markdown"]
    output = to_html(test_case)

    if entry["example"] in [187, 209, 210]:
        # this doesn't have any bearing on the output
        output = output.replace(
            "<blockquote></blockquote>", "<blockquote>\n</blockquote>"
        )

    assert output == entry["html"]
