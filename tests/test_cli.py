from io import StringIO
from pathlib import Path
from unittest import mock

import pytest

from myst_parser.cli import print_anchors
from myst_parser.mdit_to_docutils.inventory import inventory_cli

STATIC = Path(__file__).parent.absolute() / "static"


def test_print_anchors():
    in_stream = StringIO("# a\n\n## b\n\ntext")
    out_stream = StringIO()
    with mock.patch("sys.stdin", in_stream):
        with mock.patch("sys.stdout", out_stream):
            print_anchors(["-l", "1"])
    out_stream.seek(0)
    assert out_stream.read().strip() == '<h1 id="a"></h1>'


@pytest.mark.parametrize("options", [(), ("-d", "std"), ("-o", "doc"), ("-n", "ref")])
def test_read_inv(options, capsys, file_regression):
    inventory_cli([str(STATIC / "objects_v2.inv"), "-f", "yaml", *options])
    text = capsys.readouterr().out.strip() + "\n"
    file_regression.check(text, extension=".yaml")


def test_read_inv_v1(capsys, file_regression):
    inventory_cli([str(STATIC / "objects_v1.inv"), "-f", "yaml"])
    text = capsys.readouterr().out.strip() + "\n"
    file_regression.check(text, extension=".yaml")
