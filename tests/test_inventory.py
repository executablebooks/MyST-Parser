"""Test reading of inventory files."""

import json
from pathlib import Path
from urllib.request import Request

import pytest

from myst_parser import __version__
from myst_parser import inventory as myst_inventory
from myst_parser.config.main import MdParserConfig
from myst_parser.inventory import (
    USER_AGENT,
    fetch_inventory,
    filter_inventories,
    from_sphinx,
    inventory_cli,
    load,
    to_sphinx,
)

STATIC = Path(__file__).parent.absolute() / "static"
REPO_URL = "https://github.com/executablebooks/MyST-Parser"


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


class _RecordingUrlopen:
    """Stand-in for ``urllib.request.urlopen`` that records each request.

    It serves the static ``objects_v2.inv`` for URLs in ``serve``,
    and raises for any other URL (so the CLI's fallback path can be exercised).
    """

    def __init__(self, serve: set[str]):
        self.serve = serve
        self.requests: list = []

    def __call__(self, request, timeout=None):
        if isinstance(request, str):
            request = Request(request)
        self.requests.append(request)
        if request.full_url not in self.serve:
            raise OSError(f"not served: {request.full_url}")
        return (STATIC / "objects_v2.inv").open("rb")


def test_fetch_inventory_sends_user_agent(monkeypatch):
    """Remote inventories must not be fetched with urllib's default User-Agent.

    Read the Docs answers ``Python-urllib/x.y`` with HTTP 403 for every
    ``objects.inv``, so fetches identify as myst-parser instead (#1002).
    """
    url = "https://example.com/objects.inv"
    recorder = _RecordingUrlopen({url})
    monkeypatch.setattr(myst_inventory, "urlopen", recorder)
    inv = fetch_inventory(url, timeout=5)
    assert inv["objects"]
    [request] = recorder.requests
    assert request.full_url == url
    assert request.get_header("User-agent") == USER_AGENT
    assert f"myst-parser/{__version__} (+{REPO_URL})" == USER_AGENT


@pytest.mark.parametrize(
    ("uri", "served"),
    [
        ("https://example.com/objects.inv", "https://example.com/objects.inv"),
        ("https://example.com/en/latest", "https://example.com/en/latest/objects.inv"),
        ("https://example.com/en/latest/", "https://example.com/en/latest/objects.inv"),
    ],
    ids=["direct", "fallback", "fallback-trailing-slash"],
)
def test_inv_cli_sends_user_agent(uri, served, monkeypatch, capsys):
    """Every request ``myst-inv`` makes, including the fallback, sends the User-Agent."""
    recorder = _RecordingUrlopen({served})
    monkeypatch.setattr(myst_inventory, "urlopen", recorder)
    inventory_cli([uri, "-f", "json", "-n", "index"])
    output = json.loads(capsys.readouterr().out)
    assert "index" in output["objects"]["std"]["doc"]
    # the base URL is the served URL's folder, whether or not ``uri`` ended in "/"
    assert output["base_url"] == served.rsplit("/", 1)[0]
    assert recorder.requests[-1].full_url == served
    for request in recorder.requests:
        assert request.get_header("User-agent") == USER_AGENT
