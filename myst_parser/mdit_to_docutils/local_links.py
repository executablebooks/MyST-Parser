"""Handling of references to targets within the same document/project."""
from __future__ import annotations

from docutils import nodes
from docutils.transforms import Transform
from typing_extensions import TypedDict

from myst_parser._compat import findall
from myst_parser.mdit_to_docutils.inventory import (
    MystInventoryType,
    resolve_myst_inventory,
)
from myst_parser.warnings import MystWarnings, create_warning


class MystProjectLink(nodes.Element):
    """A node for a link local to the referencing document.

    It should have at least attributes:

    - `refname`
    - `refexplicit`, to indicate whether the reference text is explicit
    - `refquery` dictionary of query parameters

    """

    @property
    def refname(self) -> str:
        return self.attributes["refname"]

    @property
    def refexplicit(self) -> bool:
        return self.attributes["refexplicit"]

    @property
    def refquery(self) -> dict[str, str]:
        return self.attributes["refquery"]


class LocalAnchorType(TypedDict):
    """A dictionary of anchor information."""

    id: str
    line: int
    text: str


class MdDocumentLinks(Transform):
    """Replace markdown links [text](#ref "title").

    This is only used for docutils, sphinx handles this in a post-transform.
    """

    default_priority = 880  # same as sphinx doctree-read event / std.py process_docs

    def apply(self):

        # gather targets
        heading_anchors = gather_anchors(self.document)
        std_refs = gather_std_refs(self.document)
        # turn them into an inventory
        inventory: MystInventoryType = {
            "std": {"label": std_refs},  # type: ignore
            "myst": {"anchor": heading_anchors},  # type: ignore
        }

        # now find and resolve all local links
        link_node: MystProjectLink
        for link_node in findall(self.document)(MystProjectLink):

            ref_domain = link_node.refquery.get("d")
            ref_object_type = link_node.refquery.get("o")
            pattern_match = "pat" in link_node.refquery
            loc_str = ":".join(
                [ref_domain or "*", ref_object_type or "*", link_node.refname]
            )

            matches = resolve_myst_inventory(
                inventory,
                link_node.refname,
                has_domain=ref_domain,
                has_type=ref_object_type,
                pattern_match=pattern_match,
            )

            if not matches:
                create_warning(
                    self.document,
                    f"Unmatched local target {loc_str!r}",
                    subtype=MystWarnings.XREF_MISSING,
                    line=link_node.line,
                )
                newnode = nodes.inline()
                newnode.source, newnode.line = link_node.source, link_node.line
                newnode["classes"].append("myst-ref-error")
                if link_node.refexplicit:
                    newnode.extend(link_node.children)
                else:
                    newnode += nodes.Text(link_node.refname)
                link_node.replace_self(newnode)
                continue

            if len(matches) > 1:
                # filter out matches to anchors
                matches = [
                    m
                    for m in matches
                    if not (m.domain == "myst" and m.otype == "anchor")
                ]

            if len(matches) > 1:
                match_items = [f"'{r.domain}:{r.otype}:{r.target}'" for r in matches]
                if len(match_items) > 4:
                    match_items = match_items[:4] + ["..."]
                create_warning(
                    self.document,
                    f"Multiple targets found for {loc_str!r}: "
                    f"{','.join(match_items)}",
                    subtype=MystWarnings.XREF_DUPLICATE,
                    line=link_node.line,
                )

            # TODO sort multiple matches by priority (e.g. local first, std domain)
            ref = matches[0]

            if ref.domain == "myst" and ref.otype == "anchor":
                create_warning(
                    self.document,
                    f"Local link target 'myst:anchor:{ref.target}' "
                    "is auto-generated, so may change unexpectedly",
                    MystWarnings.XREF_NOT_EXPLICIT,
                    line=link_node.line,
                )

            reference = nodes.reference(
                refid=ref.anchor,
                internal=True,
                classes=[f"{ref.domain}-{ref.otype}", "myst-project"],
            )

            # transfer attributes to reference
            reference.source, reference.line = link_node.source, link_node.line
            if link_node["classes"]:
                reference["classes"].extend(link_node["classes"])
            if link_node.get("title"):
                reference["reftitle"] = link_node["title"]

            # add content children for the reference
            if link_node.get("refexplicit"):
                # the node may still have children, if it was an autolink
                reference += link_node.children
            elif ref.text and ref.text != "-":
                reference.append(nodes.Text(ref.text))
            else:
                # default to just showing the target
                reference.append(nodes.literal(link_node.refname, link_node.refname))

            link_node.replace_self(reference)


def gather_std_refs(document) -> dict[str, LocalAnchorType]:
    """gather all explicit target names in the document.

    this mirrors the logic in `sphinx.domains.std.StandardDomain.process_doc`
    """
    std_refs: dict[str, LocalAnchorType] = {}
    for name, explicit in document.nametypes.items():
        if not explicit:
            continue
        labelid = document.nameids[name]
        if labelid is None:
            continue
        node = document.ids[labelid]
        if isinstance(node, nodes.target) and "refid" in node:
            # indirect hyperlink targets
            node = document.ids.get(node["refid"])
            labelid = node["names"][0]
        if (
            node.tagname == "footnote"
            or "refuri" in node
            or node.tagname.startswith("desc_")
        ):
            continue

        # create the implicit text
        text = ""
        for child in node:
            if isinstance(child, (nodes.title, nodes.caption)):
                text = child.astext()
                break

        std_refs[name] = {
            "id": labelid,
            "line": node.line,
            "text": text,
        }
    return std_refs


def gather_anchors(document: nodes.document) -> dict[str, LocalAnchorType]:
    """Gather all auto-generated heading anchors in a document."""
    heading_anchors: dict[str, LocalAnchorType] = {}
    for node in findall(document)():
        try:
            anchor_name = node.get("anchor_id")
        except AttributeError:
            anchor_name = None
        if anchor_name is None:
            continue
        if anchor_name in heading_anchors:
            msg = f"skipping anchor with duplicate name {anchor_name!r}"
            line = heading_anchors[anchor_name].get("line")
            if line:
                msg += f", already set at line {line}"
            create_warning(document, msg, MystWarnings.ANCHOR_DUPE, line=node.line)
            continue

        # if absent and not clashing, add the anchor to the document
        if anchor_name not in node["ids"] and anchor_name not in document.ids:
            node["ids"].append(anchor_name)

        # get the implicit text
        text = ""
        if node.children and isinstance(node[0], nodes.title):
            text = node[0].astext()
        heading_anchors[anchor_name] = {
            "id": node["ids"][0],
            "line": node.line,
            "text": text,
        }

    return heading_anchors
