import re
from io import StringIO
from unittest import mock

from docutils import nodes
from docutils.core import publish_doctree

from myst_parser.cli import print_anchors
from myst_parser.parsers.docutils_ import Parser


def _run_cli(text: str, *args: str) -> str:
    """Run the ``myst-anchors`` CLI on ``text`` and return its output."""
    out_stream = StringIO()
    with mock.patch("sys.stdin", StringIO(text)), mock.patch("sys.stdout", out_stream):
        print_anchors(list(args))
    out_stream.seek(0)
    return out_stream.read()


def test_print_anchors():
    assert _run_cli("# a\n\n## b\n\ntext", "-l", "1").strip() == '<h1 id="a"></h1>'


def test_print_anchors_duplicates():
    """Duplicate headings are suffixed as x, x-1, x-2."""
    out = _run_cli("# a\n\n# a\n\n# a", "-l", "1")
    assert re.findall(r'id="([^"]*)"', out) == ["a", "a-1", "a-2"]


def test_print_anchors_gitlab():
    """``--slug-func gitlab`` applies the gitlab preset (digits-only -> anchor-)."""
    out = _run_cli("# 2.0", "-l", "1", "--slug-func", "gitlab")
    assert re.findall(r'id="([^"]*)"', out) == ["anchor-20"]


# a corpus exercising duplicates, dotted/digit titles, non-latin scripts,
# inline code, emphasis and internal whitespace
CROSS_CHECK_CORPUS = """\
# Dup

# Dup

# Dup

# Ubuntu 20.04

# lxc.env for environment variables

# 3rd party

# 2.0

# Привет Мир

# 中文标题

# Some `code` here

# Some *emphasis* text

# x  y
"""


def test_anchor_slugs_match_renderer():
    """Single source of truth: the CLI and the docutils renderer agree.

    The ids emitted by the ``myst-anchors`` CLI (in document order) must equal
    the ``slug`` attributes stamped on section nodes by the docutils parser.
    """
    cli_out = _run_cli(CROSS_CHECK_CORPUS, "-l", "6")
    cli_ids = re.findall(r'id="([^"]*)"', cli_out)

    doctree = publish_doctree(
        CROSS_CHECK_CORPUS,
        parser=Parser(),
        settings_overrides={"myst_heading_anchors": 6, "doctitle_xform": False},
    )
    doc_slugs = [
        section["slug"]
        for section in doctree.findall(nodes.section)
        if "slug" in section
    ]

    assert cli_ids == doc_slugs
