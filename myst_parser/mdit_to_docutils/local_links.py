"""Handling of references to targets within the same document."""
from __future__ import annotations

from typing import TYPE_CHECKING

from docutils import nodes
from docutils.transforms import Transform

from myst_parser._compat import findall
from myst_parser.mdit_to_docutils.inventory import (
    MystInventoryType,
    resolve_myst_inventory,
)
from myst_parser.warnings import MystWarnings, create_warning

if TYPE_CHECKING:
    from sphinx.environment import BuildEnvironment

    from myst_parser.sphinx_ext.references import MystDomain


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


class MdDocumentLinks(Transform):
    """Replace markdown links [text](#ref "title").

    When matching to a
    """

    default_priority = 880  # same as sphinx doctree-read event / std.py process_docs

    @property
    def sphinx_env(self) -> BuildEnvironment | None:
        return getattr(self.document.settings, "env", None)

    def apply(self):
        # import here, to avoid import loop
        from myst_parser.mdit_to_docutils.base import create_warning

        # mapping of name to target
        inventory: MystInventoryType = {}
        local_nodes: dict[tuple[str, str, str], nodes.Element] = {}

        # gather explicit target names
        # this mirrors the logic in `sphinx.domains.std.StandardDomain.process_doc`,
        # but here we want to store all specific to the docname
        for name, explicit in self.document.nametypes.items():
            if not explicit:
                continue
            labelid = self.document.nameids[name]
            if labelid is None:
                continue
            node = self.document.ids[labelid]
            if isinstance(node, nodes.target) and "refid" in node:
                # indirect hyperlink targets
                node = self.document.ids.get(node["refid"])
                labelid = node["names"][0]
            if (
                node.tagname == "footnote"
                or "refuri" in node
                or node.tagname.startswith("desc_")
            ):
                continue

            inventory.setdefault("std", {}).setdefault("label", {})[name] = {
                "id": labelid,
                "line": node.line,
                "text": None,
                "tagname": str(node.tagname or ""),
                "explicit": True,
            }
            local_nodes[("std", "label", name)] = node

        # gather heading anchors
        for node in findall(self.document)():
            try:
                anchor_name = node.get("anchor_id")
            except AttributeError:
                anchor_name = None
            if anchor_name is None:
                continue
            if anchor_name in inventory.get("myst", {}).get("anchor", {}):
                msg = f"skipping anchor with duplicate name {anchor_name!r}"
                line = inventory["myst"]["anchor"][anchor_name].get("line")
                if line:
                    msg += f", already set at line {line}"
                create_warning(
                    self.document,
                    msg,
                    MystWarnings.ANCHOR_DUPE,
                    line=node.line,
                )
                continue

            # create a unique id for the anchor and add it to the node if necessary
            anchor_id = anchor_name
            if anchor_name not in node["ids"]:
                index = 1
                while anchor_id in self.document.ids:
                    anchor_id += f"_{index}"
                    index += 1
                node["ids"].insert(0, anchor_id)

            inventory.setdefault("myst", {}).setdefault("anchor", {})[anchor_name] = {
                "id": anchor_id,
                "line": node.line,
                "text": None,
                "tagname": "anchor",
                "explicit": False,
            }
            local_nodes[("myst", "anchor", anchor_name)] = node

        # set the implicit text for all items
        for (dom, obj, name), node in local_nodes.items():
            for child in node:
                if isinstance(child, (nodes.title, nodes.caption)):
                    inventory[dom][obj][name]["text"] = child.astext()
                    break

        # if using sphinx, then save local links to the environment,
        # for use by inter-document link resolution
        if self.sphinx_env is not None:
            domain: MystDomain = self.sphinx_env.get_domain("myst")  # type: ignore
            domain.invs[self.sphinx_env.docname] = inventory

        self._resolve_links(inventory)

    def _resolve_links(self, inventory: MystInventoryType):
        """attempt to resolve project links locally"""
        node: MystProjectLink
        for node in findall(self.document)(MystProjectLink):

            ref_domain = node.refquery.get("d")
            ref_object_type = node.refquery.get("o")
            loc = ":".join([ref_domain or "*", ref_object_type or "*", node.refname])

            results = resolve_myst_inventory(
                inventory,
                ref_domain,
                ref_object_type,
                node.refname,
                "pat" in node.refquery,
            )

            # create the reference node
            if not results:
                self._handle_missing_ref(node, loc)
                continue

            if len(results) > 1:
                matches = [f"'{r.domain}:{r.otype}:{r.target}'" for r in results]
                if len(matches) > 4:
                    matches = matches[:4] + ["..."]
                create_warning(
                    self.document,
                    f"Multiple local matches found for target {loc!r}: "
                    f"{','.join(matches)}",
                    MystWarnings.XREF_DUPLICATE,
                    line=node.line,
                )

            result = results[0]

            if not result.data.get("explicit"):
                create_warning(
                    self.document,
                    f"Local link target '{result.domain}:{result.otype}:{result.target}' "
                    "is auto-generated, so may change unexpectedly",
                    MystWarnings.XREF_NOT_EXPLICIT,
                    line=node.line,
                )

            reference = nodes.reference(refid=result.anchor, internal=True)

            # transfer attributes to reference
            reference.source, reference.line = node.source, node.line
            if node["classes"]:
                reference["classes"].extend(node["classes"])
            if node.get("title"):
                reference["reftitle"] = node["title"]
            else:
                reference[
                    "reftitle"
                ] = f"{result.domain}:{result.otype}:{result.target}"

            # add content children for the reference
            if node.refexplicit:
                reference += node.children
            elif result.text:
                reference += nodes.Text(result.text)
            else:
                create_warning(
                    self.document,
                    "empty link text",
                    MystWarnings.XREF_EMPTY,
                    line=node.line,
                )
                if node.children:
                    # the node may still have children, if it was an autolink
                    reference += node.children
                else:
                    reference += nodes.Text(node.refname)

            node.replace_self(reference)

    def _handle_missing_ref(self, node: MystProjectLink, loc: str):
        """handle a missing local reference"""
        # if using sphinx, then the reference resolution is forwarded on
        # for use by inter-document link resolution
        if (not node.get("reflocal")) and (self.sphinx_env is not None):
            from sphinx.addnodes import pending_xref

            xref = pending_xref(
                # standard pending attributes
                refdoc=self.sphinx_env.docname,
                refdomain="myst",
                reftype="project",
                reftarget=node.refname,
                refexplicit=node.refexplicit,
                # myst:project specific attributes
                refquery=node.refquery,
            )
            xref.source, xref.line = node.source, node.line
            if node.get("title"):
                xref["title"] = node["title"]
            xref.children.extend(node.children)
            node.replace_self(xref)
            return

        # otherwise create a warning and replace with text of refname
        create_warning(
            self.document,
            f"Unmatched local target {loc!r}",
            subtype=MystWarnings.XREF_MISSING,
            line=node.line,
        )
        newnode = nodes.inline()
        newnode.source, newnode.line = node.source, node.line
        newnode["classes"].append("myst-ref-error")
        if node.refexplicit:
            newnode.extend(node.children)
        else:
            newnode += nodes.Text(node.refname)
        node.replace_self(newnode)
