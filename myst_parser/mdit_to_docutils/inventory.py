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
from dataclasses import dataclass
from fnmatch import fnmatchcase
from typing import IO, TYPE_CHECKING, Dict, Iterator
from urllib.request import urlopen

import yaml
from typing_extensions import TypedDict

if TYPE_CHECKING:
    from sphinx.util.typing import Inventory


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
    objects: dict[str, dict[str, dict[str, InventoryItemType]]]
    """Mapping of domain -> object type -> name -> item."""


class MystTargetType(TypedDict, total=False):
    """A reference target within a document."""

    docname: str
    """The name of the document containing the target"""
    id: str
    """The internal id of the target"""
    text: str
    """For use if no explicit text is given by the reference, e.g. the section title"""


MystInventoryType = Dict[str, Dict[str, Dict[str, MystTargetType]]]
"""Mapping of: domain -> object type -> name -> target"""


def format_inventory(inv: Inventory) -> InventoryType:
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
                "disp": text,
            }

    return {
        "name": project,
        "version": version,
        "objects": objs,
    }


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
        invdata["objects"][domain][objtype][name] = {"loc": location, "disp": "-"}

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
        invdata["objects"][domain][objtype][name] = {"loc": location, "disp": text}
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


def resolve_inventory(
    inventories: dict[str, Inventory],
    ref_target: str,
    *,
    ref_inv: None | str = None,
    ref_domain: None | str = None,
    ref_otype: None | str = None,
    match_end=False,
) -> list[InvMatch]:
    """Resolve a cross-reference in the loaded sphinx inventories.

    :param inventories: Mapping of inventory name to inventory data
    :param ref_target: The target to search for
    :param ref_inv: The name of the sphinx inventory to search, if None then
        all inventories will be searched
    :param ref_domain: The name of the domain to search, if None then all domains
        will be searched
    :param ref_otype: The type of object to search for, if None then all types will be searched
    :param match_end: Whether to match against targets that end with the ref_target

    :returns: matching results
    """
    results: list[InvMatch] = []
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

            if not match_end and ref_target in data:
                results.append(
                    InvMatch(
                        inv_name, domain_name, obj_type, ref_target, *data[ref_target]
                    )
                )
            elif match_end:
                for target in data:
                    if target.endswith(ref_target):
                        results.append(
                            InvMatch(
                                inv_name, domain_name, obj_type, target, *data[target]
                            )
                        )

    return results


@dataclass
class LocalInvMatch:
    """A match from an inventory."""

    domain: str
    otype: str
    name: str
    data: MystTargetType

    @property
    def anchor(self) -> str:
        return self.data.get("id", "")

    @property
    def text(self) -> str:
        return self.data.get("text", "")

    @property
    def docname(self) -> str:
        return self.data.get("docname", "")


def resolve_myst_inventory(
    inventory: MystInventoryType,
    ref_target: str,
    *,
    has_domain: None | str = None,
    has_type: None | str = None,
    has_docname: None | str = None,
    match_end=False,
) -> list[LocalInvMatch]:
    """Resolve a cross-reference in a document level inventory.

    :param ref_target: The target to search for
    :param has_domain: Specify a domain to filter by
    :param has_type: Specify a type of object to filter by
    :param has_docname: Specify a docname to filter by
    :param match_end: Whether to match against targets that end with the ref_target

    :returns:  matching results
    """
    results: list[LocalInvMatch] = []

    for domain_name, ddata in inventory.items():

        if has_domain is not None and has_domain != domain_name:
            continue

        for obj_type, data in ddata.items():

            if has_type is not None and has_type != obj_type:
                continue

            if not match_end and ref_target in data:
                results.append(
                    LocalInvMatch(domain_name, obj_type, ref_target, data[ref_target])
                )
            elif match_end:
                for target in data:
                    if target.endswith(ref_target):
                        results.append(
                            LocalInvMatch(domain_name, obj_type, target, data[target])
                        )

    if has_docname is not None:
        results = [r for r in results if r.docname == has_docname]

    return results


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
