"""Read an inter-sphinx inventory file (`objects.inv`).

This is adapted from the Sphinx inventory.py module.
We replicate it here, so that it can be used without Sphinx.
"""
from __future__ import annotations

import argparse
import json
import re
import zlib
from typing import IO, Iterator
from urllib.request import urlopen

import yaml
from typing_extensions import TypedDict


class InventoryItemType(TypedDict):
    """A single inventory item."""

    loc: str
    """The relative location of the item."""
    disp: str
    """Default text to display for the item."""


class InventoryType(TypedDict):
    """Inventory data."""

    name: str
    """The name of the project."""
    version: str
    """The version of the project."""
    items: dict[str, dict[str, dict[str, InventoryItemType]]]
    """Mapping of domain -> object -> name -> item."""


def load(stream: IO) -> InventoryType:
    """Load inventory data from a stream."""
    reader = InventoryFileReader(stream)
    line = reader.readline().rstrip()
    if line == "# Sphinx inventory version 1":
        return _load_v1(reader)
    elif line == "# Sphinx inventory version 2":
        return _load_v2(reader)
    else:
        raise ValueError("invalid inventory header: %s" % line)


def _load_v1(stream: InventoryFileReader) -> InventoryType:
    """Load inventory data (format v1) from a stream."""
    projname = stream.readline().rstrip()[11:]
    version = stream.readline().rstrip()[11:]
    invdata: InventoryType = {
        "name": projname,
        "version": version,
        "items": {},
    }
    for line in stream.readlines():
        name, objtype, location = line.rstrip().split(None, 2)
        # version 1 did not add anchors to the location
        domain = "py"
        if objtype == "mod":
            objtype = "module"
            location += "#module-" + name
        else:
            location += "#" + name
        invdata["items"].setdefault(domain, {}).setdefault(objtype, {})
        invdata["items"][domain][objtype][name] = {"loc": location, "disp": "-"}

    return invdata


def _load_v2(stream: InventoryFileReader) -> InventoryType:
    """Load inventory data (format v2) from a stream."""
    projname = stream.readline().rstrip()[11:]
    version = stream.readline().rstrip()[11:]
    invdata: InventoryType = {
        "name": projname,
        "version": version,
        "items": {},
    }
    line = stream.readline()
    if "zlib" not in line:
        raise ValueError("invalid inventory header (not compressed): %s" % line)

    for line in stream.read_compressed_lines():
        # be careful to handle names with embedded spaces correctly
        m = re.match(r"(?x)(.+?)\s+(\S+)\s+(-?\d+)\s+?(\S*)\s+(.*)", line.rstrip())
        if not m:
            continue
        name: str
        type: str
        name, type, _, location, dispname = m.groups()
        if ":" not in type:
            # wrong type value. type should be in the form of "{domain}:{objtype}"
            #
            # Note: To avoid the regex DoS, this is implemented in python (refs: #8175)
            continue
        if (
            type == "py:module"
            and type in invdata["items"]
            and name in invdata["items"][type]
        ):
            # due to a bug in 1.1 and below,
            # two inventory entries are created
            # for Python modules, and the first
            # one is correct
            continue
        if location.endswith("$"):
            location = location[:-1] + name
        domain, objtype = type.split(":", 1)
        invdata["items"].setdefault(domain, {}).setdefault(objtype, {})
        invdata["items"][domain][objtype][name] = {"loc": location, "disp": dispname}
    return invdata


_BUFSIZE = 16 * 1024


class InventoryFileReader:
    """A file reader for an inventory file.

    This reader supports mixture of texts and compressed texts.
    """

    def __init__(self, stream: IO) -> None:
        self.stream = stream
        self.buffer = b""
        self.eof = False

    def read_buffer(self) -> None:
        chunk = self.stream.read(_BUFSIZE)
        if chunk == b"":
            self.eof = True
        self.buffer += chunk

    def readline(self) -> str:
        pos = self.buffer.find(b"\n")
        if pos != -1:
            line = self.buffer[:pos].decode()
            self.buffer = self.buffer[pos + 1 :]
        elif self.eof:
            line = self.buffer.decode()
            self.buffer = b""
        else:
            self.read_buffer()
            line = self.readline()

        return line

    def readlines(self) -> Iterator[str]:
        while not self.eof:
            line = self.readline()
            if line:
                yield line

    def read_compressed_chunks(self) -> Iterator[bytes]:
        decompressor = zlib.decompressobj()
        while not self.eof:
            self.read_buffer()
            yield decompressor.decompress(self.buffer)
            self.buffer = b""
        yield decompressor.flush()

    def read_compressed_lines(self) -> Iterator[str]:
        buf = b""
        for chunk in self.read_compressed_chunks():
            buf += chunk
            pos = buf.find(b"\n")
            while pos != -1:
                yield buf[:pos].decode()
                buf = buf[pos + 1 :]
                pos = buf.find(b"\n")


def inventory_cli(inputs: None | list[str] = None):
    """Command line interface for fetching and parsing an inventory."""
    parser = argparse.ArgumentParser(description="Parse an inventory file.")
    parser.add_argument("uri", metavar="[URL|PATH]", help="URI of the inventory file")
    parser.add_argument(
        "-d",
        "--domain",
        metavar="DOMAIN",
        help="Filter the inventory by domain regex",
    )
    parser.add_argument(
        "-t",
        "--type",
        metavar="TYPE",
        help="Filter the inventory by object type regex",
    )
    parser.add_argument(
        "-n",
        "--name",
        metavar="NAME",
        help="Filter the inventory by reference name regex",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["yaml", "json"],
        default="yaml",
        help="Output format (default: yaml)",
    )
    args = parser.parse_args(inputs)

    if args.uri.startswith("http"):
        with urlopen(args.uri) as stream:
            invdata = load(stream)
    else:
        with open(args.uri, "rb") as stream:
            invdata = load(stream)

    # filter the inventory
    if args.domain:
        re_domain = re.compile(args.domain)
        invdata["items"] = {
            d: invdata["items"][d] for d in invdata["items"] if re_domain.fullmatch(d)
        }
    if args.type:
        re_type = re.compile(args.type)
        for domain in list(invdata["items"]):
            invdata["items"][domain] = {
                t: invdata["items"][domain][t]
                for t in invdata["items"][domain]
                if re_type.fullmatch(t)
            }
    if args.name:
        re_name = re.compile(args.name)
        for domain in invdata["items"]:
            for otype in list(invdata["items"][domain]):
                invdata["items"][domain][otype] = {
                    n: invdata["items"][domain][otype][n]
                    for n in invdata["items"][domain][otype]
                    if re_name.fullmatch(n)
                }

    # clean up empty items
    for domain in list(invdata["items"]):
        for otype in list(invdata["items"][domain]):
            if not invdata["items"][domain][otype]:
                del invdata["items"][domain][otype]
        if not invdata["items"][domain]:
            del invdata["items"][domain]

    if args.format == "json":
        print(json.dumps(invdata, indent=2, sort_keys=False))
    else:
        print(yaml.dump(invdata, sort_keys=False))


if __name__ == "__main__":
    inventory_cli()
