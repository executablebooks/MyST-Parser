from unittest import mock

from myst_parser.cli import print_anchors


def test_print_anchors():
    from io import StringIO

    in_stream = StringIO("# a\n\n## b\n\ntext")
    out_stream = StringIO()
    with mock.patch("sys.stdin", in_stream):
        with mock.patch("sys.stdout", out_stream):
            print_anchors(["-l", "1"])
    out_stream.seek(0)
    assert out_stream.read().strip() == '<h1 id="a"></h1>'
