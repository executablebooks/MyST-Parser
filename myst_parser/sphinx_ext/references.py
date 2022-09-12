"""A post-transform for overriding the behaviour of sphinx reference resolution.

This is applied to MyST type references only, such as ``[text](myst:target)``
"""
from __future__ import annotations

import os
import re
from copy import copy
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
from sphinx.util.texescape import tex_replace_map

from myst_parser.mdit_to_docutils.inventory import (
    LocalInvMatch,
    MystInventoryType,
    format_inventory,
    resolve_inventory,
    resolve_myst_inventory,
)
from myst_parser.mdit_to_docutils.local_links import (
    LocalAnchorType,
    gather_anchors,
    inventory_search_args,
)
from myst_parser.warnings import MystWarnings

LOGGER = logging.getLogger(__name__)


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

    @property
    def std_figtypes(self) -> dict[str, dict[str, tuple[str, str]]]:
        """The per document mapping of std:label name -> (node_id, enumtype)."""
        return self.data.setdefault("std_figtypes", {})

    @property
    def inventory(self) -> MystInventoryType:
        """The project wide MyST references, by domain -> object type."""
        return self.data.setdefault("inventory", {})

    def process_doc(
        self, env: BuildEnvironment, docname: str, document: nodes.document
    ) -> None:
        self.anchors[docname] = gather_anchors(document)

        # gather std:label figure types
        # this replicates some functionality from StandardDomain._resolve_numref_xref
        # but there one has to load the whole document every time, which is slow!
        # We store it, for later use by the patched StandardDomain.get_object_enum
        std: StandardDomain = env.get_domain("std")  # type: ignore
        self.std_figtypes[docname] = {}
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
            figtype = std.get_enumerable_node_type(node)
            if figtype:
                self.std_figtypes[docname][name] = (node["ids"][0], figtype)

    def clear_doc(self, docname: str) -> None:
        self.anchors.pop(docname, None)
        self.std_figtypes.pop(docname, None)

    def merge_domaindata(self, docnames: list[str], otherdata: dict) -> None:
        for docname in docnames:
            self.anchors[docname] = otherdata["anchors"][docname]
            self.std_figtypes[docname] = otherdata["std_figtypes"][docname]

    def get_object_enum(
        self, docname: str, object_type: str, name: str
    ) -> tuple[str | None, str | None]:
        """Get the (enum type, number) for an object in this domain."""
        if object_type != "anchor":
            return None, None

        result = self.anchors.get(docname, {}).get(name)
        if not result:
            return None, None

        if docname not in self.env.toc_secnumbers:
            return None, None  # no number assigned

        anchorname = "#" + result["id"]
        if anchorname not in self.env.toc_secnumbers[docname]:
            # try first heading which has no anchor
            num = self.env.toc_secnumbers[docname].get("")
        else:
            num = self.env.toc_secnumbers[docname].get(anchorname)

        if num is None:
            return None, None

        return "section", ".".join(map(str, num))

    def update_project_inventory(self) -> None:
        """Build the inventory for the project, and update anchor numbers.

        For numbering, this should be run after `TocTreeCollector.get_updated_docs`,
        i.e. after `env-get-updated` event, priority 500.
        """
        LOGGER.info("Updating MyST inventory")

        self.inventory.clear()

        # update inventory with all available domain data
        for domainname, domain in sorted(self.env.domains.items()):
            for name, text, otype, docname, anchor, __ in sorted(domain.get_objects()):
                self.inventory.setdefault(domainname, {}).setdefault(otype, {})[
                    name
                ] = {
                    "id": anchor,
                    "docname": docname,
                }
                # genindex/search have this as a tuple
                if isinstance(text, str) and text:
                    self.inventory[domainname][otype][name]["text"] = text

        # now also add the math domain, which is not yet included in the inventory
        # see: https://github.com/sphinx-doc/sphinx/issues/9483
        math: MathDomain = self.env.get_domain("math")  # type: ignore
        if not math.get_objects():
            for label, (docname, __) in math.equations.items():
                node_id = nodes.make_id(f"equation-{label}")
                self.inventory.setdefault("math", {}).setdefault("label", {})
                self.inventory["math"]["label"][label] = {
                    "id": node_id,
                    "docname": docname,
                }


class MystRefrenceResolver(SphinxPostTransform):
    """A post-transform for overriding the behaviour of myst reference resolution."""

    # run before the sphinx reference resolver
    default_priority = ReferencesResolver.default_priority - 1

    def run(self, **kwargs: Any) -> None:

        myst: MystDomain = self.env.get_domain("myst")  # type: ignore

        for node in self.document.findall(pending_xref):

            if node.get("refdomain") != "myst":
                continue

            typ = node.get("reftype")

            newnode: Element | None = None
            if typ == "project":
                newnode = self._resolve_xref_project(node, myst.inventory)
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
        ref_docname: None | str = node.get("reftargetdoc")

        if not node["reftarget"] and ref_docname:
            return self._resolve_xref_doc(node, ref_docname)

        ref_target, ref_domain, ref_object_type, match_end = inventory_search_args(
            node["reftarget"], node.get("refquery", "")
        )

        # get matches from the project inventory
        loc_str = ":".join(
            [ref_domain or "*", ref_object_type or "*", node["reftarget"]]
        )
        matches = resolve_myst_inventory(
            inventory,
            ref_target,
            has_domain=ref_domain,
            has_type=ref_object_type,
            has_docname=ref_docname,
            match_end=match_end,
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
                if (match_end and anchor_name.endswith(ref_target)) or (
                    not match_end and anchor_name == ref_target
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
            match_items = [f"'{r.domain}:{r.otype}:{r.name}'" for r in matches]
            if len(match_items) > 4:
                match_items = match_items[:4] + ["..."]
            log_warning(
                f"Multiple targets found for {loc_str!r}{doc_str}: "
                f"{','.join(match_items)}",
                subtype=MystWarnings.XREF_DUPLICATE,
                location=node,
            )

        # TODO sort multiple matches by priority (e.g. local first, std domain)
        target = matches[0]

        if target.domain == "myst" and target.otype == "anchor":
            log_warning(
                f"Link target 'myst:anchor:{target.name}' in doc {anchor_docname!r} "
                f"is auto-generated, so may change unexpectedly",
                subtype=MystWarnings.XREF_NOT_EXPLICIT,
                location=node,
            )

        ref_node = nodes.reference(
            "", "", internal=True, classes=[f"{target.domain}-{target.otype}"]
        )
        if (
            self.app.builder.name == "latex"
            and target.domain == "math"
            and target.otype == "label"
        ):
            # The latex builder replaces math xrefs with math_reference nodes,
            # which always makes the reference name `equation:{docname}:{target}`
            # we need to make the reference be output as that
            # TODO make this less hacky?
            ref_node["refuri"] = f"%equation:{target.docname}#{target.name}"
        if target.docname == node["refdoc"]:
            ref_node["refid"] = target.anchor
        else:
            try:
                refuri = self.app.builder.get_relative_uri(
                    node["refdoc"], target.docname
                )
            except NoUri:
                log_warning(
                    "No URI available for this builder",
                    subtype=MystWarnings.XREF_ERROR,
                    location=node,
                )
                return None
            if target.anchor:
                refuri += "#" + target.anchor
            ref_node["refuri"] = refuri

        # attempt to retrieve a number for the reference
        enum_type, number = domain_get_object_enum(
            self.env.get_domain(target.domain),
            target.docname,
            target.otype,
            target.name,
        )
        # attempt to match the enum type to a prefix or default to the enum type
        prefix = self.config.myst_link_prefixes.get(enum_type, enum_type)

        # add content children
        if node.get("refexplicit"):
            # show the text explicity given by the user, maybe replacing placeholders
            ref_node += node.children
            if self.config.myst_link_placeholders:
                if self.app.builder.name == "latex":
                    self._replace_placeholders_latex(
                        ref_node, target, enum_type, prefix, number
                    )
                else:
                    self._replace_placeholders(
                        ref_node, target, enum_type, prefix, number
                    )
        elif target.text and target.text != "-":
            # show the implicit text provided by the target
            ref_node.append(nodes.Text(target.text))
        else:
            # default to just showing the objects name as literal
            ref_node.append(nodes.literal(target.name, target.name))

        return ref_node

    def _replace_placeholders(
        self,
        node: Element,
        ref: LocalInvMatch,
        etype: str | None = None,
        prefix: str | None = None,
        number: str | None = None,
    ) -> None:
        """Replace placeholders in a nodes text."""
        placeholders = {
            "{name}": ref.text,
            "{number}": number,
            "{type}": etype,
            "{Type}": etype.capitalize() if etype else "",
            "{prefix}": prefix,
            "{Prefix}": prefix.capitalize() if prefix else "",
        }
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
        etype: str | None = None,
        prefix: str | None = None,
        number: str | None = None,
    ) -> None:
        """Replace placeholders in a nodes text, for latex builder.

        As opposed to the other builder, the latex builder lets latex handle
        the numbering.
        """
        identifier = f"{ref.docname}:{ref.anchor}"
        if ref.domain == "math" and ref.otype == "label":
            # The latex builder replaces math xrefs with math_reference nodes,
            # which always makes the reference name `equation:{docname}:{target}`
            identifier = f"equation:{ref.docname}:{ref.name}"
        # apply `sphinx.writers.latex.LaTexTranslator.idescape` to the identifier
        identifier = r"\detokenize{%s}" % str(identifier).translate(
            tex_replace_map
        ).encode("ascii", "backslashreplace").decode("ascii").replace("\\", "_")
        placeholders = {
            "{name}": f"\\nameref{{{identifier}}}",
            "{number}": f"\\ref{{{identifier}}}",
            "{type}": etype,
            "{Type}": etype.capitalize() if etype else "",
            "{prefix}": prefix,
            "{Prefix}": prefix.capitalize() if prefix else "",
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
            # show the text explicity given by the user
            ref_node.extend(node.children)
        else:
            # use the document title
            text = clean_astext(self.env.titles[docname])
            ref_node.append(nodes.Text(text))

        return ref_node

    def _resolve_xref_inventory(
        self,
        node: pending_xref,
    ) -> Element | None:
        """Resolve a cross-reference to an object in a sphinx inventory."""
        ref_inv = node.get("refkey", "") or None
        ref_target, ref_domain, ref_object_type, match_end = inventory_search_args(
            node["reftarget"], node.get("refquery", "")
        )

        if ref_inv and ref_inv not in InventoryAdapter(self.env).named_inventory:
            log_warning(
                f"Unknown inventory {ref_inv!r}",
                subtype=MystWarnings.IREF_MISSING,
                location=node,
            )
            return None

        results = resolve_inventory(
            InventoryAdapter(self.env).named_inventory,
            ref_target,
            ref_inv=ref_inv,
            ref_domain=ref_domain,
            ref_otype=ref_object_type,
            match_end=match_end,
        )
        loc = ":".join(
            [
                ref_inv or "*",
                ref_domain or "*",
                ref_object_type or "*",
                node["reftarget"],
            ]
        )
        if not results:
            log_warning(
                f"Unmatched target {loc!r}",
                subtype=MystWarnings.IREF_MISSING,
                location=node,
            )
            return None
        if len(results) > 1:
            matches = [f"'{r.inv}:{r.domain}:{r.otype}:{r.name}'" for r in results]
            if len(matches) > 4:
                matches = matches[:4] + ["..."]
            log_warning(
                f"Multiple targets found for {loc!r}: {','.join(matches)}",
                subtype=MystWarnings.IREF_DUPLICATE,
                location=node,
            )
            return None

        target = results[0]

        if "://" not in target.uri and node.get("refdoc"):
            # get correct path in case of subdirectories
            target.uri = os.path.join(relative_path(node["refdoc"], "."), target.uri)

        if target.version:
            reftitle = _("(in %s v%s)") % (target.proj, target.version)
        else:
            reftitle = _("(in %s)") % (target.proj,)

        res_node = nodes.reference(
            "",
            "",
            internal=False,
            refuri=target.uri,
            reftitle=reftitle,
            classes=[f"{target.domain}-{target.otype}"],
        )

        # add content children
        if node.get("refexplicit"):
            # show the text explicity given by the user
            res_node.extend(node.children)
        elif target.text and target.text != "-":
            # use the object's implicit text
            res_node.append(nodes.Text(target.text))
        else:
            # use the object's name and show as literal
            res_node.append(nodes.literal(target.name, target.name))

        return res_node


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


def domain_get_object_enum(
    dom: Domain, docname: str, otype: str, name: str
) -> tuple[str | None, str | None]:
    """Return the (enum_type, number) for a Domain instance.

    This searches for `get_object_enum` method on the domain, and if it exists,
    calls it with the given arguments.

    For the std and math domains, we use a custom implementation of this method.
    """
    if isinstance(dom, StandardDomain):
        return _get_object_enum_std(dom, docname, otype, name)
    elif isinstance(dom, MathDomain):
        return _get_object_enum_math(dom, docname, otype, name)
    method = getattr(dom, "get_object_enum", None)
    if method is None:
        return None, None
    return method(docname, otype, name)


def _get_object_enum_std(
    self: StandardDomain, docname: str, otype: str, name: str
) -> tuple[str | None, str | None]:
    """Return the (enum_type, number) for a StandardDomain object.

    This replicates code from `sphinx.domains.math.get_fignumber`,
    but looks up the `node_id` and `figtype` from a mapping stored by the MystDomain,
    so that we don't have to incur expensive loadings of the doctree.
    """
    if otype != "label":
        return None, None
    myst_domain: MystDomain = self.env.get_domain("myst")  # type: ignore
    if docname not in myst_domain.std_figtypes:
        return None, None
    if name not in myst_domain.std_figtypes[docname]:
        return None, None
    node_id, figtype = myst_domain.std_figtypes[docname][name]
    num = None
    if figtype == "section":
        if docname not in self.env.toc_secnumbers:
            return None, None  # no number assigned
        else:
            anchorname = "#" + node_id
            if anchorname not in self.env.toc_secnumbers[docname]:
                # try first heading which has no anchor
                num = self.env.toc_secnumbers[docname].get("")
            else:
                num = self.env.toc_secnumbers[docname].get(anchorname)
    else:
        try:
            num = self.env.toc_fignumbers[docname][figtype][node_id]
        except (KeyError, IndexError):
            # target_node is found, but fignumber is not assigned.
            pass
    if num is None:
        return None, None
    return figtype, ".".join(map(str, num))


def _get_object_enum_math(
    self: MathDomain, docname: str, otype: str, name: str
) -> tuple[str | None, str | None]:
    """Return the (enum_type, number) for a MathDomain object.

    This replicates code from `sphinx.domains.math.resolve_xref`
    """
    if otype != "label":
        return None, None
    if name not in self.equations:
        return None, None
    docname, number = self.equations[name]
    node_id = nodes.make_id("equation-%s" % name)
    if self.env.config.math_numfig and self.env.config.numfig:
        if docname in self.env.toc_fignumbers:
            numbers = self.env.toc_fignumbers[docname]["displaymath"].get(node_id, ())
            eqno = ".".join(map(str, numbers))
        else:
            return None, None
    else:
        eqno = str(number)

    return "equation", eqno


class MystReferencesBuilder(DummyBuilder):
    """A builder that outputs YAML mappings of anchor/project/external references."""

    name = "myst_refs"
    epilog = "Build finished. See files in: %(outdir)s"

    def finish(self) -> None:

        myst: MystDomain = self.env.get_domain("myst")  # type: ignore

        # add enumerable data to the inventory data
        project_inv: dict = {}
        for domain_name, ddata in myst.inventory.items():
            dom = self.env.get_domain(domain_name)
            for otype_name, odata in ddata.items():
                for name, ndata in odata.items():
                    idata = project_inv.setdefault(domain_name, {}).setdefault(
                        otype_name, {}
                    )
                    idata[name] = copy(ndata)
                    enumtype, number = domain_get_object_enum(
                        dom, ndata["docname"], otype_name, name
                    )
                    if enumtype:
                        idata[name]["enumtype"] = enumtype
                    if number:
                        idata[name]["number"] = number

        # project references
        project_data = {
            "name": self.config.project,
            "version": self.config.version,
            "objects": project_inv,
        }
        with open(os.path.join(self.outdir, "project.yaml"), "w") as f:
            yaml.dump(project_data, f, sort_keys=False)

        # local references
        # add enumerable data to the anchor data
        anchor_data: dict = {}
        for docname, docdata in myst.anchors.items():
            for name, adata in docdata.items():
                anchor_data.setdefault(docname, {})[name] = copy(adata)
                enumtype, number = myst.get_object_enum(docname, "anchor", name)
                if enumtype:
                    anchor_data[docname][name]["enumtype"] = enumtype
                if number:
                    anchor_data[docname][name]["number"] = number
        with open(os.path.join(self.outdir, "anchors.yaml"), "w") as f:
            yaml.dump(anchor_data, f, sort_keys=True)

        # external inventories
        for name, inv in InventoryAdapter(self.env).named_inventory.items():
            with open(os.path.join(self.outdir, f"inv.{name}.yaml"), "w") as f:
                inv_data = format_inventory(inv)
                yaml.dump(inv_data, f, sort_keys=False)
