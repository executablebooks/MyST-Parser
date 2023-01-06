"""Logic for dealing with sphinx style inventories (e.g. `objects.inv`).

These contain mappings of reference names to ids, scoped by domain and object type.

This is adapted from the Sphinx inventory.py module.
We replicate it here, so that it can be used without Sphinx.
"""
from __future__ import annotations

import argparse
import json
import re
import zlib
from dataclasses import asdict, dataclass
from fnmatch import fnmatchcase
from typing import IO, TYPE_CHECKING, Iterator
from urllib.request import urlopen

import yaml

from ._compat import TypedDict

if TYPE_CHECKING:
    from sphinx.util.typing import Inventory


class InventoryItemType(TypedDict):
    """A single inventory item."""

    loc: str
    """The relative location of the item."""
    text: str | None
    """Implicit text to show for the item."""


class InventoryType(TypedDict):
    """Inventory data."""

    name: str
    """The name of the project."""
    version: str
    """The version of the project."""
    objects: dict[str, dict[str, dict[str, InventoryItemType]]]
    """Mapping of domain -> object type -> name -> item."""


def from_sphinx(inv: Inventory) -> InventoryType:
    """Convert a Sphinx inventory to one that is JSON compliant."""
    project = ""
    version = ""
    objs: dict[str, dict[str, dict[str, InventoryItemType]]] = {}
    for domain_obj_name, data in inv.items():
        if ":" not in domain_obj_name:
            continue

        domain_name, obj_type = domain_obj_name.split(":", 1)
        objs.setdefault(domain_name, {}).setdefault(obj_type, {})
        for refname, refdata in data.items():
            project, version, uri, text = refdata
            objs[domain_name][obj_type][refname] = {
                "loc": uri,
                "text": None if (not text or text == "-") else text,
            }

    return {
        "name": project,
        "version": version,
        "objects": objs,
    }


def to_sphinx(inv: InventoryType) -> Inventory:
    """Convert a JSON compliant inventory to one that is Sphinx compliant."""
    objs: Inventory = {}
    for domain_name, obj_types in inv["objects"].items():
        for obj_type, refs in obj_types.items():
            for refname, refdata in refs.items():
                objs.setdefault(f"{domain_name}:{obj_type}", {})[refname] = (
                    inv["name"],
                    inv["version"],
                    refdata["loc"],
                    refdata["text"] or "-",
                )
    return objs


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
        "objects": {},
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
        invdata["objects"].setdefault(domain, {}).setdefault(objtype, {})
        invdata["objects"][domain][objtype][name] = {"loc": location, "text": None}

    return invdata


def _load_v2(stream: InventoryFileReader) -> InventoryType:
    """Load inventory data (format v2) from a stream."""
    projname = stream.readline().rstrip()[11:]
    version = stream.readline().rstrip()[11:]
    invdata: InventoryType = {
        "name": projname,
        "version": version,
        "objects": {},
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
        name, type, _, location, text = m.groups()
        if ":" not in type:
            # wrong type value. type should be in the form of "{domain}:{objtype}"
            #
            # Note: To avoid the regex DoS, this is implemented in python (refs: #8175)
            continue
        if (
            type == "py:module"
            and type in invdata["objects"]
            and name in invdata["objects"][type]
        ):
            # due to a bug in 1.1 and below,
            # two inventory entries are created
            # for Python modules, and the first
            # one is correct
            continue
        if location.endswith("$"):
            location = location[:-1] + name
        domain, objtype = type.split(":", 1)
        invdata["objects"].setdefault(domain, {}).setdefault(objtype, {})
        if not text or text == "-":
            text = None
        invdata["objects"][domain][objtype][name] = {"loc": location, "text": text}
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


@dataclass
class InvMatch:
    """A match from an inventory."""

    inv: str
    domain: str
    otype: str
    name: str
    proj: str
    version: str
    uri: str
    text: str

    def asdict(self) -> dict[str, str]:
        return asdict(self)


def filter_inventories(
    inventories: dict[str, Inventory],
    ref_target: str,
    *,
    ref_inv: None | str = None,
    ref_domain: None | str = None,
    ref_otype: None | str = None,
    fnmatch_target=False,
) -> Iterator[InvMatch]:
    """Resolve a cross-reference in the loaded sphinx inventories.

    :param inventories: Mapping of inventory name to inventory data
    :param ref_target: The target to search for
    :param ref_inv: The name of the sphinx inventory to search, if None then
        all inventories will be searched
    :param ref_domain: The name of the domain to search, if None then all domains
        will be searched
    :param ref_otype: The type of object to search for, if None then all types will be searched
    :param fnmatch_target: Whether to match ref_target using fnmatchcase

    :yields: matching results
    """
    for inv_name, inv_data in inventories.items():

        if ref_inv is not None and ref_inv != inv_name:
            continue

        for domain_obj_name, data in inv_data.items():

            if ":" not in domain_obj_name:
                continue

            domain_name, obj_type = domain_obj_name.split(":", 1)

            if ref_domain is not None and ref_domain != domain_name:
                continue

            if ref_otype is not None and ref_otype != obj_type:
                continue

            if not fnmatch_target and ref_target in data:
                yield (
                    InvMatch(
                        inv_name, domain_name, obj_type, ref_target, *data[ref_target]
                    )
                )
            elif fnmatch_target:
                for target in data:
                    if fnmatchcase(target, ref_target):
                        yield (
                            InvMatch(
                                inv_name, domain_name, obj_type, target, *data[target]
                            )
                        )


def inventory_cli(inputs: None | list[str] = None):
    """Command line interface for fetching and parsing an inventory."""
    parser = argparse.ArgumentParser(description="Parse an inventory file.")
    parser.add_argument("uri", metavar="[URL|PATH]", help="URI of the inventory file")
    parser.add_argument(
        "-d",
        "--domain",
        metavar="DOMAIN",
        help="Filter the inventory by domain pattern",
    )
    parser.add_argument(
        "-o",
        "--object-type",
        metavar="TYPE",
        help="Filter the inventory by object type pattern",
    )
    parser.add_argument(
        "-n",
        "--name",
        metavar="NAME",
        help="Filter the inventory by reference name pattern",
    )
    parser.add_argument(
        "-l",
        "--loc",
        metavar="LOC",
        help="Filter the inventory by reference location pattern",
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
        try:
            with urlopen(args.uri) as stream:
                invdata = load(stream)
        except Exception:
            with urlopen(args.uri + "/objects.inv") as stream:
                invdata = load(stream)
    else:
        with open(args.uri, "rb") as stream:
            invdata = load(stream)

    # filter the inventory
    if args.domain:
        invdata["objects"] = {
            d: invdata["objects"][d]
            for d in invdata["objects"]
            if fnmatchcase(d, args.domain)
        }
    if args.object_type:
        for domain in list(invdata["objects"]):
            invdata["objects"][domain] = {
                t: invdata["objects"][domain][t]
                for t in invdata["objects"][domain]
                if fnmatchcase(t, args.object_type)
            }
    if args.name:
        for domain in invdata["objects"]:
            for otype in list(invdata["objects"][domain]):
                invdata["objects"][domain][otype] = {
                    n: invdata["objects"][domain][otype][n]
                    for n in invdata["objects"][domain][otype]
                    if fnmatchcase(n, args.name)
                }

    if args.loc:
        for domain in invdata["objects"]:
            for otype in list(invdata["objects"][domain]):
                invdata["objects"][domain][otype] = {
                    n: i
                    for n, i in invdata["objects"][domain][otype].items()
                    if fnmatchcase(i["loc"], args.loc)
                }

    # clean up empty items
    for domain in list(invdata["objects"]):
        for otype in list(invdata["objects"][domain]):
            if not invdata["objects"][domain][otype]:
                del invdata["objects"][domain][otype]
        if not invdata["objects"][domain]:
            del invdata["objects"][domain]

    if args.format == "json":
        print(json.dumps(invdata, indent=2, sort_keys=False))
    else:
        print(yaml.dump(invdata, sort_keys=False))


if __name__ == "__main__":
    inventory_cli()
