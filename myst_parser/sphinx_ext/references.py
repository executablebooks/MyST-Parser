"""A post-transform for overriding the behaviour of sphinx reference resolution.

This is applied to MyST type references only, such as ``[text](myst:target)``
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

import yaml
from docutils import nodes
from docutils.nodes import Element
from docutils.utils import relative_path
from sphinx.addnodes import pending_xref
from sphinx.builders.dummy import DummyBuilder
from sphinx.errors import NoUri
from sphinx.ext.intersphinx import InventoryAdapter
from sphinx.locale import _
from sphinx.transforms.post_transforms import ReferencesResolver, SphinxPostTransform
from sphinx.util import logging
from sphinx.util.nodes import clean_astext

from myst_parser.mdit_to_docutils.inventory import (
    ResoleInventoryDupeError,
    ResoleInventoryMissingError,
    format_inventory,
    resolve_inventory,
)
from myst_parser.mdit_to_docutils.local_links import MystLocalTarget
from myst_parser.warnings import MystWarnings

if TYPE_CHECKING:
    from sphinx.util.typing import Inventory

LOGGER = logging.getLogger(__name__)


def log_warning(
    msg: str, subtype: MystWarnings, location: None | Element, once: None | bool = None
) -> None:
    """Log a warning message."""
    # TODO bypass reference warnings if not nitpicky?
    optional = {}
    if location is not None:
        optional["location"] = location
    if once is not None:
        optional["once"] = once
    LOGGER.warning(
        f"{msg} [myst.{subtype.value}]",
        type="myst",
        subtype=subtype.value,
        **optional,
    )


class MystRefrenceResolver(SphinxPostTransform):
    """A post-transform for overriding the behaviour of myst reference resolution."""

    # run before the sphinx reference resolver
    default_priority = ReferencesResolver.default_priority - 1

    def run(self, **kwargs: Any) -> None:

        # lazy load the inventory, if we find a reference to it
        inventory: None | Inventory = None

        for node in self.document.findall(pending_xref):

            if node.get("refdomain") != "myst":
                continue

            typ = node.get("reftype")

            newnode: Element | None = None
            if typ == "doc":
                newnode = self._resolve_xref_doc(node)
            elif typ == "local":
                newnode = self._resolve_xref_local(node)
            elif typ == "project":
                if inventory is None:
                    inventory = self._project_inventory()
                newnode = self._resolve_xref_project(node, inventory)
            elif typ == "inv":
                newnode = self._resolve_xref_inventory(node)
            else:
                log_warning(
                    f"Unknown reference type {typ!r}",
                    location=node,
                    subtype=MystWarnings.XREF_TYPE,
                )

            # create a placeholder, for failed resolutions
            if newnode is None:
                newnode = nodes.inline()
                newnode["classes"].append("myst-ref-error")
                if node.children:
                    newnode.extend(node.children)
                else:
                    newnode += nodes.Text(node["reftarget"])

            # add myst class to all references
            if newnode:
                newnode["classes"].append(f"myst-{typ}")

            # always override the title, if an explicit title is given
            if newnode and node.get("title"):
                newnode["reftitle"] = node["title"]

            newnode.source = node.source
            newnode.line = node.line
            node.replace_self(newnode)

    def _project_inventory(self) -> Inventory:
        """Build the inventory for this project."""
        inventory: Inventory = {}
        for domainname, domain in sorted(self.env.domains.items()):
            for name, dispname, otype, docname, anchor, __ in sorted(
                domain.get_objects()
            ):
                # TODO this is a bit of a hack, putting docname in place of version
                # so we can re-use the resolve_inventory function
                inventory.setdefault(f"{domainname}:{otype}", {})[name] = (
                    "",
                    docname,
                    anchor,
                    dispname,
                )
        return inventory

    def _resolve_xref_project(
        self,
        node: pending_xref,
        inventory: Inventory,
    ) -> Element | None:
        """Resolve a cross-reference to an object within this project."""
        # get search variables
        ref_query = node.get("refquery", {})
        ref_domain = ref_query.get("d")
        ref_object_type = ref_query.get("o")
        ref_target = node["reftarget"]
        ref_pattern = "pat" in ref_query

        try:
            res = resolve_inventory(
                {"local": inventory},
                "local",
                ref_domain,
                ref_object_type,
                ref_target,
                ref_pattern,
            )
        except ResoleInventoryMissingError as exc:
            log_warning(
                str(exc),
                subtype=MystWarnings.XREF_MISSING,
                location=node,
            )
            return None
        except ResoleInventoryDupeError as exc:
            log_warning(
                str(exc),
                subtype=MystWarnings.XREF_DUPLICATE,
                location=node,
            )
            return None

        docname = res.version
        anchor = res.uri

        res_node = nodes.reference("", "", internal=True)
        if docname == node["refdoc"]:
            res_node["refid"] = anchor
        else:
            try:
                refuri = self.app.builder.get_relative_uri(node["refdoc"], docname)
            except NoUri:
                log_warning(
                    "No URI available for this builder",
                    subtype=MystWarnings.XREF_ERROR,
                    location=node,
                )
                return None
            if anchor:
                refuri += "#" + anchor
            res_node["refuri"] = refuri

        # add a title, so we can capture what the match was in the output
        res_node["reftitle"] = f"myst:project:{res.domain}:{res.otype}"

        # add content children
        if node.get("refexplicit"):
            res_node += node.children
        elif not res.dispname or res.dispname == "-":
            res_node.append(nodes.literal(res.target, res.target))
        else:
            res_node.append(nodes.Text(res.dispname))

        return res_node

    def _resolve_xref_inventory(
        self,
        node: pending_xref,
    ) -> Element | None:
        """Resolve a cross-reference to an object in a sphinx inventory."""

        # get search variables
        ref_query = node.get("refquery", {})
        ref_inv = ref_query.get("i")
        ref_domain = ref_query.get("d")
        ref_object_type = ref_query.get("o")
        ref_target = node["reftarget"]
        ref_pattern = "pat" in ref_query

        try:
            res = resolve_inventory(
                InventoryAdapter(self.env).named_inventory,
                ref_inv,
                ref_domain,
                ref_object_type,
                ref_target,
                ref_pattern,
            )
        except ResoleInventoryMissingError as exc:
            log_warning(
                str(exc),
                subtype=MystWarnings.IREF_MISSING,
                location=node,
            )
            return None
        except ResoleInventoryDupeError as exc:
            log_warning(
                str(exc),
                subtype=MystWarnings.IREF_DUPLICATE,
                location=node,
            )
            return None

        if "://" not in res.uri and node.get("refdoc"):
            # get correct path in case of subdirectories
            res.uri = os.path.join(relative_path(node["refdoc"], "."), res.uri)

        if res.version:
            reftitle = _("(in %s v%s)") % (res.proj, res.version)
        else:
            reftitle = _("(in %s)") % (res.proj,)

        res_node = nodes.reference(
            "", "", internal=False, refuri=res.uri, reftitle=reftitle
        )
        # add a class, so we can capture what the match was in the output
        res_node["classes"].append(f"inv-{res.inv}-{res.domain}-{res.otype}")

        # add content children
        if node.get("refexplicit"):
            res_node.extend(node.children)
        elif res.dispname == "-":
            res_node.append(nodes.literal(res.target, res.target))
        else:
            res_node.append(nodes.Text(res.dispname))

        return res_node

    def _resolve_xref_doc(
        self,
        node: pending_xref,
    ) -> Element | None:
        """Resolve a cross-reference another document within the project,
        and optionally a target within it.
        """
        docname: str = node["reftarget"]
        refname: str = node["refquery"].get("t", "")
        return self._resolve_xref_doc_target(node, docname, refname)

    def _resolve_xref_local(
        self,
        node: pending_xref,
    ) -> Element | None:
        """Resolve a cross-reference to a target within the current document."""
        docname: str = node["refdoc"]
        refname: str = node["reftarget"]
        return self._resolve_xref_doc_target(node, docname, refname)

    def _resolve_xref_doc_target(
        self,
        node: pending_xref,
        docname: str,
        refname: str,
    ) -> Element | None:
        """Resolve a cross-reference to a document and (optional) target."""
        # check that the docname can be found
        if docname not in self.env.all_docs:
            log_warning(
                f"Unknown reference docname {docname!r}",
                location=node,
                subtype=MystWarnings.XREF_MISSING,
            )
            return None

        # find the the id for the refname, if given
        refid = ""
        reftext: str | None = None
        if refname:
            myst_refs: dict[str, MystLocalTarget] = self.env.metadata[docname].get(
                "myst_local_targets", {}
            )
            if refname not in myst_refs:
                log_warning(
                    f"Unknown ref {refname!r} in doc {docname!r}",
                    location=node,
                    subtype=MystWarnings.XREF_MISSING,
                )
                return None
            refid = myst_refs[refname]["id"]
            reftext = myst_refs[refname]["text"]

        ref_node = nodes.reference("", "", internal=True)
        if node["refdoc"] == docname and refid:
            ref_node["refid"] = refid
        else:
            try:
                refuri = self.app.builder.get_relative_uri(node["refdoc"], docname)
            except NoUri:
                log_warning(
                    "No URI available for this builder",
                    subtype=MystWarnings.XREF_ERROR,
                    location=node,
                )
                return None
            if refid:
                refuri += "#" + refid
            ref_node["refuri"] = refuri

        # add content children
        if node.get("refexplicit"):
            ref_node.extend(node.children)
        elif not refname:
            # use the document title
            text = clean_astext(self.env.titles[docname])
            ref_node.append(nodes.Text(text))
        elif reftext:
            # use the display text given for the reference
            ref_node.append(nodes.Text(reftext))
        else:
            # default to just showing the target
            log_warning(
                "empty link text",
                location=node,
                subtype=MystWarnings.XREF_EMPTY,
            )
            ref_node.append(nodes.Text(f"{docname}#{refname}"))

        return ref_node


class MystReferencesBuilder(DummyBuilder):
    """A builder that outputs YAML mappings of local/project/external references."""

    name = "myst_refs"
    epilog = "Build finished. See files in: %(outdir)s"

    def finish(self) -> None:

        # local references
        local_data: dict = {}
        for docname, data in self.env.metadata.items():
            local_data.setdefault(docname, {})
            doc_data: dict[str, MystLocalTarget] = data.get("myst_local_targets", {})
            for ref_data in doc_data.values():
                local_data[docname].setdefault(ref_data["type"], {})
                local_data[docname][ref_data["type"]][ref_data["name"]] = {
                    "id": ref_data["id"],
                    "line": ref_data["line"],
                    "text": ref_data["text"],
                }

        with open(os.path.join(self.outdir, "local.yaml"), "w") as f:
            yaml.dump(local_data, f, sort_keys=True)

        # project references
        data = {
            "name": self.config.project,
            "version": self.config.version,
            "objects": {},
        }
        objects = data["objects"]
        for domainname, domain in sorted(self.env.domains.items()):
            for name, dispname, otype, docname, anchor, __ in sorted(
                domain.get_objects()
            ):
                objects.setdefault(domainname, {})
                objects[domainname].setdefault(otype, {})
                objects[domainname][otype][name] = {
                    "docname": docname,
                    "anchor": anchor,
                }
                if isinstance(dispname, str) and dispname != name:
                    objects[domainname][otype][name]["dispname"] = dispname
        with open(os.path.join(self.outdir, "project.yaml"), "w") as f:
            yaml.dump(data, f, sort_keys=False)

        # external inventories
        for name, inv in InventoryAdapter(self.env).named_inventory.items():
            with open(os.path.join(self.outdir, f"inv.{name}.yaml"), "w") as f:
                inv_data = format_inventory(inv)
                yaml.dump(inv_data, f, sort_keys=False)
