"""Test reading of inventory files."""
from pathlib import Path

import pytest

from myst_parser.inventory import filter_inventories, inventory_cli, load, to_sphinx

STATIC = Path(__file__).parent.absolute() / "static"


def test_inv_resolve(data_regression):
    with (STATIC / "objects_v2.inv").open("rb") as f:
        inv = to_sphinx(load(f))
    output = [m.asdict() for m in filter_inventories({"inv": inv}, "index")]
    data_regression.check(output)


def test_inv_resolve_fnmatch(data_regression):
    with (STATIC / "objects_v2.inv").open("rb") as f:
        inv = to_sphinx(load(f))
    output = [
        m.asdict()
        for m in filter_inventories({"inv": inv}, "*index", fnmatch_target=True)
    ]
    data_regression.check(output)


@pytest.mark.parametrize("options", [(), ("-d", "std"), ("-o", "doc"), ("-n", "ref")])
def test_inv_cli_v2(options, capsys, file_regression):
    inventory_cli([str(STATIC / "objects_v2.inv"), "-f", "yaml", *options])
    text = capsys.readouterr().out.strip() + "\n"
    file_regression.check(text, extension=".yaml")


def test_inv_cli_v1(capsys, file_regression):
    inventory_cli([str(STATIC / "objects_v1.inv"), "-f", "yaml"])
    text = capsys.readouterr().out.strip() + "\n"
    file_regression.check(text, extension=".yaml")
