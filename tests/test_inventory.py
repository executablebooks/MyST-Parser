"""Test reading of inventory files."""
from pathlib import Path

import pytest

from myst_parser.config.main import MdParserConfig
from myst_parser.inventory import (
    filter_inventories,
    from_sphinx,
    inventory_cli,
    load,
    to_sphinx,
)

STATIC = Path(__file__).parent.absolute() / "static"


@pytest.mark.parametrize(
    "value",
    [
        None,
        {1: 2},
        {"key": 1},
        {"key": [1, 2]},
        {"key": ["a", 1]},
    ],
)
def test_docutils_config_invalid(value):
    with pytest.raises((TypeError, ValueError)):
        MdParserConfig(inventories=value)


def test_convert_roundtrip():
    with (STATIC / "objects_v2.inv").open("rb") as f:
        inv = load(f)
    assert inv == from_sphinx(to_sphinx(inv))


def test_inv_filter(data_regression):
    with (STATIC / "objects_v2.inv").open("rb") as f:
        inv = load(f)
    output = [m.asdict() for m in filter_inventories({"inv": inv}, targets="index")]
    data_regression.check(output)


def test_inv_filter_wildcard(data_regression):
    with (STATIC / "objects_v2.inv").open("rb") as f:
        inv = load(f)
    output = [m.asdict() for m in filter_inventories({"inv": inv}, targets="*index")]
    data_regression.check(output)


@pytest.mark.parametrize(
    "options", [(), ("-d", "std"), ("-o", "doc"), ("-n", "ref"), ("-l", "index.html*")]
)
def test_inv_cli_v2(options, capsys, file_regression):
    inventory_cli([str(STATIC / "objects_v2.inv"), "-f", "yaml", *options])
    text = capsys.readouterr().out.strip() + "\n"
    file_regression.check(text, extension=".yaml")


def test_inv_cli_v1(capsys, file_regression):
    inventory_cli([str(STATIC / "objects_v1.inv"), "-f", "yaml"])
    text = capsys.readouterr().out.strip() + "\n"
    file_regression.check(text, extension=".yaml")
