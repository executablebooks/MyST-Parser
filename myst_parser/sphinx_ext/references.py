"""A post-transform for overriding the behaviour of sphinx reference resolution.

This is applied to MyST type references only, such as ``[text](myst:target)``
"""
from __future__ import annotations

import os
from typing import Any

import yaml
from docutils import nodes
from docutils.nodes import Element
from docutils.utils import relative_path
from sphinx.addnodes import pending_xref
from sphinx.builders.dummy import DummyBuilder
from sphinx.domains import Domain
from sphinx.domains.math import MathDomain
from sphinx.domains.std import StandardDomain
from sphinx.environment import BuildEnvironment
from sphinx.errors import NoUri
from sphinx.ext.intersphinx import InventoryAdapter
from sphinx.locale import _
from sphinx.transforms.post_transforms import ReferencesResolver, SphinxPostTransform
from sphinx.util import logging
from sphinx.util.nodes import clean_astext

from myst_parser.mdit_to_docutils.inventory import (
    MystInventoryType,
    MystTargetType,
    format_inventory,
    resolve_inventory,
    resolve_myst_inventory,
)
from myst_parser.warnings import MystWarnings

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


class MystDomain(Domain):
    """A sphinx domain for MyST references.

    Here we store the per document inventories for the project.
    """

    name = "myst"
    label = "MyST"

    def resolve_any_xref(self, *args, **kwargs):
        # this must be implemented, but we don't use it
        return []

    @property
    def invs(self) -> dict[str, MystInventoryType]:
        """The per document inventories."""
        return self.data.setdefault("invs", {})

    def process_doc(
        self, env: BuildEnvironment, docname: str, document: nodes.document
    ) -> None:
        pass

    def clear_doc(self, docname: str) -> None:
        self.invs.pop(docname, None)

    def merge_domaindata(self, docnames: list[str], otherdata: dict) -> None:
        for docname in docnames:
            self.invs[docname] = otherdata["invs"][docname]


def project_inventory(env: BuildEnvironment) -> MystInventoryType:
    """Build the inventory for this project."""
    # get the data for the standard inventory
    inventory: MystInventoryType = {}
    for domainname, domain in sorted(env.domains.items()):
        for name, dispname, otype, docname, anchor, __ in sorted(domain.get_objects()):
            inventory.setdefault(domainname, {}).setdefault(otype, {})[name] = {
                "id": anchor,
                "docname": docname,
            }
            # genindex/search have this as a tuple
            if isinstance(dispname, str) and dispname:
                inventory[domainname][otype][name]["text"] = dispname
    # now also add the math domain, which is not yet included in the inventory
    # see: https://github.com/sphinx-doc/sphinx/issues/9483
    math: MathDomain = env.get_domain("math")  # type: ignore
    if not math.get_objects():
        for label, (docname, __) in math.equations.items():
            node_id = nodes.make_id(f"equation-{label}")
            inventory.setdefault("math", {}).setdefault("label", {})
            inventory["math"]["label"][label] = {
                "id": node_id,
                "docname": docname,
            }

    # assign numbers to standard labels
    std: StandardDomain = env.get_domain("std")  # type: ignore

    class _Builder(DummyBuilder):
        """`std.get_fignumber` skips latex builders,
        but here we don't actually want to do that, so we use a dummy builder
        """

        def __init__(self) -> None:
            pass

    _builder = _Builder()

    # categorise by docname
    doc_label: dict[str, list[MystTargetType]] = {}
    for item in inventory.get("std", {}).get("label", {}).values():
        docname = item.get("docname", "")
        if docname:
            doc_label.setdefault(docname, []).append(item)
    for docname, labels in doc_label.items():
        # we only run if there are actually labels to assign,
        # as loading documents is costly
        if not (env.toc_secnumbers.get(docname) or env.toc_fignumbers.get(docname)):
            continue
        doc = env.get_doctree(docname)
        for item in labels:
            target_node = doc.ids.get(item["id"])
            if target_node is None:
                continue
            figtype = std.get_enumerable_node_type(target_node)
            if not figtype:
                continue
            try:
                num = std.get_fignumber(env, _builder, figtype, docname, target_node)
            except ValueError:
                continue
            if not num:
                continue
            item["number"] = ".".join(map(str, num))

    return inventory


class MystRefrenceResolver(SphinxPostTransform):
    """A post-transform for overriding the behaviour of myst reference resolution."""

    # run before the sphinx reference resolver
    default_priority = ReferencesResolver.default_priority - 1

    def run(self, **kwargs: Any) -> None:

        # lazy load the inventory, if we find a reference to it
        inventory: None | MystInventoryType = None

        for node in self.document.findall(pending_xref):

            if node.get("refdomain") != "myst":
                continue

            typ = node.get("reftype")

            newnode: Element | None = None
            if typ == "doc":
                newnode = self._resolve_xref_document(node)
            elif typ == "project":
                if inventory is None:
                    inventory = project_inventory(self.env)
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

    def _resolve_xref_project(
        self,
        node: pending_xref,
        inventory: MystInventoryType,
    ) -> Element | None:
        """Resolve a cross-reference to an object within this project."""
        # get search variables
        ref_query = node.get("refquery", {})
        ref_domain = ref_query.get("d")
        ref_object_type = ref_query.get("o")
        ref_target = node["reftarget"]
        ref_pattern = "pat" in ref_query

        results = resolve_myst_inventory(
            inventory,
            ref_domain,
            ref_object_type,
            ref_target,
            ref_pattern,
        )
        loc = ":".join([ref_domain or "*", ref_object_type or "*", ref_target])
        if not results:
            log_warning(
                f"Unmatched target {loc!r}",
                subtype=MystWarnings.XREF_MISSING,
                location=node,
            )
            return None
        if len(results) > 1:
            matches = [f"'{r.domain}:{r.otype}:{r.target}'" for r in results]
            if len(matches) > 4:
                matches = matches[:4] + ["..."]
            log_warning(
                f"Multiple matches found for target {loc!r}: {','.join(matches)}",
                subtype=MystWarnings.XREF_DUPLICATE,
                location=node,
            )

        result = results[0]

        res_node = nodes.reference(
            "", "", internal=True, classes=[f"{result.domain}-{result.otype}"]
        )
        if (
            self.app.builder.name == "latex"
            and result.domain == "math"
            and result.otype == "label"
        ):
            # The latex builder replaces math xrefs with math_reference nodes,
            # which always makes the reference name `equation:{docname}:{target}`
            # we need to make the reference be output as that
            # TODO make this less hacky?
            res_node["refuri"] = f"%equation:{result.docname}#{result.anchor[9:]}"
        if result.docname == node["refdoc"]:
            res_node["refid"] = result.anchor
        else:
            try:
                refuri = self.app.builder.get_relative_uri(
                    node["refdoc"], result.docname
                )
            except NoUri:
                log_warning(
                    "No URI available for this builder",
                    subtype=MystWarnings.XREF_ERROR,
                    location=node,
                )
                return None
            if result.anchor:
                refuri += "#" + result.anchor
            res_node["refuri"] = refuri

        # add a title, so we can capture what the match was in the output
        res_node["reftitle"] = f"myst:project:{result.domain}:{result.otype}"

        # add content children
        if node.get("refexplicit"):
            res_node += node.children
        elif not result.text or result.text == "-":
            res_node.append(nodes.literal(result.target, result.target))
        else:
            res_node.append(nodes.Text(result.text))

        return res_node

    def _resolve_xref_inventory(
        self,
        node: pending_xref,
    ) -> Element | None:
        """Resolve a cross-reference to an object in a sphinx inventory."""

        # get search variables
        ref_query = node.get("refquery", {})
        ref_inv = node.get("refkey", "") or None
        ref_domain = ref_query.get("d")
        ref_object_type = ref_query.get("o")
        ref_target = node["reftarget"]
        ref_pattern = "pat" in ref_query

        if ref_inv and ref_inv not in InventoryAdapter(self.env).named_inventory:
            log_warning(
                f"Unknown inventory {ref_inv!r}",
                subtype=MystWarnings.IREF_MISSING,
                location=node,
            )
            return None

        results = resolve_inventory(
            InventoryAdapter(self.env).named_inventory,
            ref_inv,
            ref_domain,
            ref_object_type,
            ref_target,
            ref_pattern,
        )
        loc = ":".join(
            [ref_inv or "*", ref_domain or "*", ref_object_type or "*", ref_target]
        )
        if not results:
            log_warning(
                f"Unmatched target {loc!r}",
                subtype=MystWarnings.IREF_MISSING,
                location=node,
            )
            return None
        if len(results) > 1:
            matches = [f"'{r.inv}:{r.domain}:{r.otype}:{r.target}'" for r in results]
            if len(matches) > 4:
                matches = matches[:4] + ["..."]
            log_warning(
                f"Multiple matches found for target {loc!r}: {','.join(matches)}",
                subtype=MystWarnings.IREF_DUPLICATE,
                location=node,
            )
            return None

        res = results[0]

        if "://" not in res.uri and node.get("refdoc"):
            # get correct path in case of subdirectories
            res.uri = os.path.join(relative_path(node["refdoc"], "."), res.uri)

        if res.version:
            reftitle = _("(in %s v%s)") % (res.proj, res.version)
        else:
            reftitle = _("(in %s)") % (res.proj,)

        res_node = nodes.reference(
            "",
            "",
            internal=False,
            refuri=res.uri,
            reftitle=reftitle,
            classes=[f"{res.domain}-{res.otype}"],
        )

        # add content children
        if node.get("refexplicit"):
            res_node.extend(node.children)
        elif res.dispname == "-":
            res_node.append(nodes.literal(res.target, res.target))
        else:
            res_node.append(nodes.Text(res.dispname))

        return res_node

    def _resolve_xref_document(
        self,
        node: pending_xref,
    ) -> Element | None:
        """Resolve a cross-reference to a document and (optional) target."""
        docname = node["reftargetdoc"]
        refname = node["reftarget"]
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
            # get search variables
            ref_query = node.get("refquery", {})
            ref_domain = ref_query.get("d")
            ref_object_type = ref_query.get("o")
            ref_pattern = "pat" in ref_query
            inventory: MystInventoryType = self.env.domaindata["myst"]["invs"][docname]
            results = resolve_myst_inventory(
                inventory, ref_domain, ref_object_type, refname, ref_pattern
            )
            loc = ":".join([ref_domain or "*", ref_object_type or "*", refname])
            if not results:
                log_warning(
                    f"Unmatched target {loc!r} in doc {docname!r}",
                    location=node,
                    subtype=MystWarnings.XREF_MISSING,
                )
                return None
            if len(results) > 1:
                matches = [f"'{r.domain}:{r.otype}:{r.target}'" for r in results]
                if len(matches) > 4:
                    matches = matches[:4] + ["..."]
                log_warning(
                    f"Multiple matches found for target {loc!r} in doc {docname!r}: "
                    f"{','.join(matches)}",
                    location=node,
                    subtype=MystWarnings.XREF_DUPLICATE,
                )
            result = results[0]
            if result.data.get("implicit"):
                log_warning(
                    f"Link target '{result.domain}:{result.otype}:{result.target}' "
                    f"in doc {docname!r} is auto-generated, so may change unexpectedly",
                    MystWarnings.XREF_NOT_EXPLICIT,
                    location=node,
                )
            refid = result.anchor
            reftext = result.text
            classes = [f"{result.domain}-{result.otype}"]
        else:
            classes = ["doc"]

        ref_node = nodes.reference("", "", internal=True, classes=classes)
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
        dom: MystDomain = self.env.get_domain("myst")  # type: ignore
        with open(os.path.join(self.outdir, "local.yaml"), "w") as f:
            yaml.dump(dom.invs, f, sort_keys=True)

        # project references
        data = {
            "name": self.config.project,
            "version": self.config.version,
            "objects": project_inventory(self.env),
        }
        with open(os.path.join(self.outdir, "project.yaml"), "w") as f:
            yaml.dump(data, f, sort_keys=False)

        # external inventories
        for name, inv in InventoryAdapter(self.env).named_inventory.items():
            with open(os.path.join(self.outdir, f"inv.{name}.yaml"), "w") as f:
                inv_data = format_inventory(inv)
                yaml.dump(inv_data, f, sort_keys=False)
