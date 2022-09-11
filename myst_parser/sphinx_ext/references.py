"""A post-transform for overriding the behaviour of sphinx reference resolution.

This is applied to MyST type references only, such as ``[text](myst:target)``
"""
from __future__ import annotations

import os
import re
from fnmatch import fnmatchcase
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
    LocalInvMatch,
    MystInventoryType,
    MystTargetType,
    format_inventory,
    resolve_inventory,
    resolve_myst_inventory,
)
from myst_parser.mdit_to_docutils.local_links import LocalAnchorType, gather_anchors
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
    def anchors(self) -> dict[str, dict[str, LocalAnchorType]]:
        """The per document mapping of auto-generated heading anchors."""
        return self.data.setdefault("anchors", {})

    def process_doc(
        self, env: BuildEnvironment, docname: str, document: nodes.document
    ) -> None:
        self.anchors[docname] = gather_anchors(document)

    def clear_doc(self, docname: str) -> None:
        self.anchors.pop(docname, None)

    def merge_domaindata(self, docnames: list[str], otherdata: dict) -> None:
        for docname in docnames:
            self.anchors[docname] = otherdata["anchors"][docname]


def project_inventory(env: BuildEnvironment, with_numbers: bool) -> MystInventoryType:
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
        for label, (docname, number) in math.equations.items():
            node_id = nodes.make_id(f"equation-{label}")
            inventory.setdefault("math", {}).setdefault("label", {})
            inventory["math"]["label"][label] = {
                "id": node_id,
                "docname": docname,
            }

            # get number
            numbers = (
                env.toc_fignumbers.get(docname, {})
                .get("displaymath", {})
                .get(node_id, None)
            )
            if env.config.math_numfig and env.config.numfig:
                if numbers:
                    inventory["math"]["label"][label]["number"] = ".".join(
                        map(str, numbers)
                    )
                else:
                    inventory["math"]["label"][label]["number"] = ""
            else:
                inventory["math"]["label"][label]["number"] = str(number)

    if not with_numbers:
        return inventory

    # assign numbers to standard labels and anchors
    std: StandardDomain = env.get_domain("std")  # type: ignore
    myst: MystDomain = env.get_domain("myst")  # type: ignore

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
    for docname, items in myst.anchors.items():
        doc_label.setdefault(docname, []).extend(list(items.values()))  # type: ignore
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
        # TODO move this loading to env-check-consistency event (store on MystDomain?)
        # so that we are not running it for every document
        inventory: None | MystInventoryType = None

        for node in self.document.findall(pending_xref):

            if node.get("refdomain") != "myst":
                continue

            typ = node.get("reftype")

            newnode: Element | None = None
            if typ == "project":
                if inventory is None:
                    inventory = project_inventory(
                        self.env, with_numbers=self.env.config.myst_link_placeholders
                    )
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

    def _resolve_xref_doc(
        self,
        node: pending_xref,
        docname: str,
    ) -> Element | None:
        """Resolve a reference to a document."""
        if docname not in self.env.all_docs:
            log_warning(
                f"Unknown reference docname {docname!r}",
                location=node,
                subtype=MystWarnings.XREF_MISSING,
            )
            return None

        ref_node = nodes.reference("", "", internal=True, classes=["doc"])

        try:
            ref_node["refuri"] = self.app.builder.get_relative_uri(
                node["refdoc"], docname
            )
        except NoUri:
            log_warning(
                "No URI available for this builder",
                subtype=MystWarnings.XREF_ERROR,
                location=node,
            )
            return None

        # add content children
        if node.get("refexplicit"):
            ref_node.extend(node.children)
        else:
            # use the document title
            text = clean_astext(self.env.titles[docname])
            ref_node.append(nodes.Text(text))

        return ref_node

    def _resolve_xref_project(
        self,
        node: pending_xref,
        inventory: MystInventoryType,
    ) -> Element | None:
        """Resolve a cross-reference to an object within this project."""
        # get search variables
        ref_query: dict[str, str] = node.get("refquery", {})
        ref_domain = ref_query.get("d")
        ref_object_type = ref_query.get("o")
        ref_target: str = node["reftarget"]
        ref_docname: None | str = node.get("reftargetdoc")
        ref_pattern = "pat" in ref_query

        if not ref_target and ref_docname:
            return self._resolve_xref_doc(node, ref_docname)

        # get matches from the project inventory
        loc_str = ":".join([ref_domain or "*", ref_object_type or "*", ref_target])
        matches = resolve_myst_inventory(
            inventory,
            ref_target,
            has_domain=ref_domain,
            has_type=ref_object_type,
            has_docname=ref_docname,
            pattern_match=ref_pattern,
        )

        # if there are no inventory matches, look at any auto-generated (implicit) labels
        if (
            not matches
            and (ref_domain is None or ref_domain == "myst")
            and (ref_object_type is None or ref_object_type == "anchor")
        ):
            anchor_docname = ref_docname or node["refdoc"]
            myst_domain: MystDomain = self.env.get_domain("myst")  # type: ignore
            for anchor_name, anchor_data in myst_domain.anchors.get(
                anchor_docname, {}
            ).items():
                if (ref_pattern and fnmatchcase(anchor_name, ref_target)) or (
                    not ref_pattern and anchor_name == ref_target
                ):
                    matches.append(
                        LocalInvMatch(
                            "myst",
                            "anchor",
                            anchor_name,
                            {
                                "docname": anchor_docname,
                                "id": anchor_data["id"],
                                "text": anchor_data["text"],
                                "number": anchor_data.get("number", ""),  # type: ignore
                            },
                        )
                    )

        # handle none or multiple matches
        doc_str = f" in doc {ref_docname!r}" if ref_docname else ""
        if not matches:
            log_warning(
                f"Unmatched target {loc_str!r}{doc_str}",
                subtype=MystWarnings.XREF_MISSING,
                location=node,
            )
            return None
        if len(matches) > 1:
            match_items = [f"'{r.domain}:{r.otype}:{r.target}'" for r in matches]
            if len(match_items) > 4:
                match_items = match_items[:4] + ["..."]
            log_warning(
                f"Multiple targets found for {loc_str!r}{doc_str}: "
                f"{','.join(match_items)}",
                subtype=MystWarnings.XREF_DUPLICATE,
                location=node,
            )

        # TODO sort multiple matches by priority (e.g. local first, std domain)
        ref = matches[0]

        if ref.domain == "myst" and ref.otype == "anchor":
            log_warning(
                f"Link target 'myst:anchor:{ref_target}' in doc {anchor_docname!r} "
                f"is auto-generated, so may change unexpectedly",
                subtype=MystWarnings.XREF_NOT_EXPLICIT,
                location=node,
            )

        ref_node = nodes.reference(
            "", "", internal=True, classes=[f"{ref.domain}-{ref.otype}"]
        )
        if (
            self.app.builder.name == "latex"
            and ref.domain == "math"
            and ref.otype == "label"
        ):
            # The latex builder replaces math xrefs with math_reference nodes,
            # which always makes the reference name `equation:{docname}:{target}`
            # we need to make the reference be output as that
            # TODO make this less hacky?
            ref_node["refuri"] = f"%equation:{ref.docname}#{ref.target}"
        if ref.docname == node["refdoc"]:
            ref_node["refid"] = ref.anchor
        else:
            try:
                refuri = self.app.builder.get_relative_uri(node["refdoc"], ref.docname)
            except NoUri:
                log_warning(
                    "No URI available for this builder",
                    subtype=MystWarnings.XREF_ERROR,
                    location=node,
                )
                return None
            if ref.anchor:
                refuri += "#" + ref.anchor
            ref_node["refuri"] = refuri

        # add content children
        if node.get("refexplicit"):
            ref_node += node.children
            if self.config.myst_link_placeholders:
                if self.app.builder.name == "latex":
                    self._replace_placeholders_latex(ref_node, ref)
                else:
                    self._replace_placeholders(ref_node, ref)
        elif ref.text and ref.text != "-":
            ref_node.append(nodes.Text(ref.text))
        else:
            # default to just showing the target
            ref_node.append(nodes.literal(ref.target, ref.target))

        return ref_node

    def _replace_placeholders(
        self,
        node: Element,
        ref: LocalInvMatch,
    ) -> None:
        """Replace placeholders in a nodes text."""
        placeholders = {"{name}": ref.text, "{number}": ref.number}
        regex = re.compile(f"({'|'.join(placeholders)})")

        for child in node.findall(nodes.Text):
            final = ""
            for piece in regex.split(child.astext()):
                if piece in placeholders:
                    value = placeholders[piece]
                    if not value:
                        log_warning(
                            f"{piece!r} replacement is not available",
                            subtype=MystWarnings.XREF_PLACEHOLDER,
                            location=node,
                        )
                        final += "?"
                    else:
                        final += value
                else:
                    final += piece
            child.parent.replace(child, nodes.Text(final))

    def _replace_placeholders_latex(
        self,
        node: Element,
        ref: LocalInvMatch,
    ) -> None:
        """Replace placeholders in a nodes text, for latex builder."""

        if ref.domain == "math" and ref.otype == "label":
            # The latex builder replaces math xrefs with math_reference nodes,
            # which always prepend this
            placeholders = {
                "{name}": f"\\nameref{{equation:{ref.docname}:{ref.target}}}",
                "{number}": f"\\ref{{equation:{ref.docname}:{ref.target}}}",
            }
        else:
            placeholders = {
                "{name}": f"\\nameref{{{ref.docname}:{ref.anchor}}}",
                "{number}": f"\\ref{{{ref.docname}:{ref.anchor}}}",
            }
        regex = re.compile(f"({'|'.join(placeholders)})")

        for child in node.findall(nodes.Text):
            components = []
            for piece in regex.split(child.astext()):
                if piece in placeholders:
                    if not placeholders[piece]:
                        log_warning(
                            f"{piece!r} replacement not available",
                            subtype=MystWarnings.XREF_PLACEHOLDER,
                            location=node,
                        )
                    else:
                        components.append(
                            nodes.raw(
                                placeholders[piece], placeholders[piece], format="latex"
                            )
                        )
                elif piece:
                    components.append(nodes.Text(piece))
            child.parent.replace(child, components)

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
                f"Multiple targets found for {loc!r}: {','.join(matches)}",
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


class MystReferencesBuilder(DummyBuilder):
    """A builder that outputs YAML mappings of local/project/external references."""

    name = "myst_refs"
    epilog = "Build finished. See files in: %(outdir)s"

    def finish(self) -> None:

        # project references
        data = {
            "name": self.config.project,
            "version": self.config.version,
            "objects": project_inventory(self.env, with_numbers=True),
        }
        with open(os.path.join(self.outdir, "project.yaml"), "w") as f:
            yaml.dump(data, f, sort_keys=False)

        # local references (call after project_inventory, to populate numbers)
        dom: MystDomain = self.env.get_domain("myst")  # type: ignore
        with open(os.path.join(self.outdir, "anchors.yaml"), "w") as f:
            yaml.dump(dom.anchors, f, sort_keys=True)

        # external inventories
        for name, inv in InventoryAdapter(self.env).named_inventory.items():
            with open(os.path.join(self.outdir, f"inv.{name}.yaml"), "w") as f:
                inv_data = format_inventory(inv)
                yaml.dump(inv_data, f, sort_keys=False)
