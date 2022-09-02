"""A post-transform for overriding the behaviour of sphinx reference resolution.

This is applied to MyST type references only, such as ``[text](target)``,
and allows for nested syntax
"""
from __future__ import annotations

from contextlib import suppress
from itertools import product
from typing import TYPE_CHECKING, cast

from docutils import nodes
from docutils.nodes import Element
from sphinx.addnodes import pending_xref
from sphinx.domains import Domain
from sphinx.domains.std import StandardDomain
from sphinx.errors import NoUri
from sphinx.util import docname_join, logging
from sphinx.util.nodes import clean_astext, make_refnode

from myst_parser.transforms.local_links import MystLocalTarget
from myst_parser.warnings import MystWarnings

if TYPE_CHECKING:
    from sphinx.builders import Builder
    from sphinx.environment import BuildEnvironment

LOGGER = logging.getLogger(__name__)


def log_warning(
    msg: str, subtype: MystWarnings, location: None | Element, once: None | bool = None
) -> None:
    """Log a warning message."""
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


class MystRefDomain(Domain):
    name = "myst"
    label = "MyST references"

    def merge_domaindata(self, docnames: list[str], otherdata: dict) -> None:
        # mut be implemented
        pass

    def resolve_any_xref(
        self,
        env: BuildEnvironment,
        fromdocname: str,
        builder: Builder,
        target: str,
        node: pending_xref,
        contnode: Element,
    ) -> list[tuple[str, Element]]:
        # must be implemented
        return []

    def resolve_xref(
        self,
        env: BuildEnvironment,
        fromdocname: str,
        builder: Builder,
        typ: str,
        target: str,
        node: pending_xref,
        contnode: Element,
    ) -> Element | None:
        newnode: Element | None = None
        if typ == "any":
            newnode = self._resolve_xref_any(env, fromdocname, builder, node, contnode)
        elif typ == "doc":
            newnode = self._resolve_xref_doc(env, fromdocname, builder, node, contnode)
        elif typ == "project":
            newnode = self._resolve_xref_project(
                env, fromdocname, builder, node, contnode
            )
        elif typ == "inv":
            newnode = self._resolve_xref_inventory(
                env, fromdocname, builder, node, contnode
            )
        else:
            log_warning(
                f"Unknown reference type {typ!r}",
                location=node,
                subtype=MystWarnings.XREF_TYPE,
            )

        # always override the title, if an explicit title is given
        if newnode and node.get("title"):
            newnode["reftitle"] = node["title"]

        # always return a node, so that sphinx does not emit its own warnings
        return newnode or contnode

    def _resolve_xref_project(
        self,
        env: BuildEnvironment,
        fromdocname: str,
        builder: Builder,
        node: pending_xref,
        contnode: Element,
    ) -> Element | None:
        """Resolve a cross-reference within this project.

        This is similar to use of the `std:ref` role,
        but also allows for nested parsing of text.
        """
        target = node["reftarget"]
        stddomain = cast(StandardDomain, self.env.get_domain("std"))
        newnode = stddomain._resolve_ref_xref(
            env, fromdocname, builder, "ref", target, node, contnode
        )
        if newnode is None:
            log_warning(
                f"Unknown project reference {target!r}",
                location=node,
                subtype=MystWarnings.XREF_MISSING,
            )
            return None
        if node["refexplicit"]:
            # replace children of the new node with those of the contnode
            # and make classes similar to those produced by `std:ref` role
            with suppress(ValueError):
                contnode["classes"].remove("xref")
            contnode["classes"].extend(["std", "std-ref"])
            newnode.children = [contnode]

        return newnode

    def _resolve_xref_inventory(
        self,
        env: BuildEnvironment,
        fromdocname: str,
        builder: Builder,
        node: pending_xref,
        contnode: Element,
    ) -> Element | None:
        """Resolve a cross-reference to an intersphinx inventory."""

        # get search variables
        refquery = node.get("refquery", {})
        inv_name = refquery.get("name")
        refdomain = refquery.get("domain")
        reftype = refquery.get("type")
        reftarget = node["reftarget"]

        # Ensure the node has content, based on its target
        # we then set refexplicit, to stop the intersphinx function from overriding
        if not node["refexplicit"]:
            label = nodes.literal(reftarget, reftarget)
            contnode.append(label)
            node["refexplicit"] = True

        return resolve_intersphinx(env, node, contnode, inv_name, refdomain, reftype)

    def _resolve_xref_doc(
        self,
        env: BuildEnvironment,
        fromdocname: str,
        builder: Builder,
        node: pending_xref,
        contnode: Element,
    ) -> Element | None:
        """Resolve a cross-reference to another document within the project,
        and possibly a target within it.
        """
        docname: str = docname_join(fromdocname, node["reftarget"])
        refname: str | None = node.get("refname", None)

        # check that the docname can be found
        if docname not in env.all_docs:
            log_warning(
                f"Unknown reference docname {docname!r}",
                location=node,
                subtype=MystWarnings.XREF_MISSING,
            )
            return None

        # find the the id for the a fragment, if given
        refid = ""
        reftext: str | None = None
        if refname:
            myst_refs: dict[str, dict] = env.metadata[docname].get(
                "myst_local_targets", {}
            )
            if refname not in myst_refs:
                log_warning(
                    f"Unknown local ref {refname!r} in doc {docname!r}",
                    location=node,
                    subtype=MystWarnings.XREF_MISSING,
                )
            else:
                ref = MystLocalTarget(**myst_refs[refname])
                refid = ref.id
                reftext = ref.text

        # if the reference has no child content, try to replace with the relevant text
        if not contnode.children:
            if refname and refid:
                text = reftext or ""
                if not text:
                    log_warning(
                        "empty link text",
                        location=node,
                        subtype=MystWarnings.XREF_EMPTY,
                    )
            else:
                text = clean_astext(env.titles[docname])
            contnode = nodes.inline(text, text, classes=contnode["classes"])

        # make classes similar to those produced by `doc` role
        with suppress(ValueError):
            contnode["classes"].remove("xref")
        if "doc" not in contnode["classes"]:
            contnode["classes"].append("doc")

        return make_refnode(
            builder, fromdocname, docname, refid, contnode, node.get("title")
        )

    def _resolve_xref_any(
        self,
        env: BuildEnvironment,
        fromdocname: str,
        builder: Builder,
        node: pending_xref,
        contnode: Element,
    ) -> Element | None:
        """Resolve a cross-reference to anything available.

        This is similar to the use of the `any` role,
        """
        target: str = node["reftarget"]
        refdoc = node.get("refdoc")
        refquery = node.get("refquery", {})
        # get allowed domains for referencing
        # ref_domains = self.env.config.myst_ref_domains
        ref_domains = [refquery["domain"]] if "domain" in refquery else None

        results: list[tuple[str, Element]] = []

        # we make the `std` domain a priority
        if ref_domains is None or "std" in ref_domains:
            stddomain = cast(StandardDomain, self.env.get_domain("std"))

            results.extend(
                stddomain.resolve_any_xref(
                    self.env, refdoc, builder, target, node, contnode
                )
            )
            # also try resolving as a docname
            doc_ref = stddomain.resolve_xref(
                self.env, refdoc, builder, "doc", target, node, contnode
            )
            if doc_ref:
                results.append(("doc", doc_ref))

        for domain in self.env.domains.values():
            if domain.name == "std":
                continue  # we did this one already
            if ref_domains is not None and domain.name not in ref_domains:
                continue
            try:
                results.extend(
                    domain.resolve_any_xref(
                        self.env, refdoc, builder, target, node, contnode
                    )
                )
            except NotImplementedError:
                if not (getattr(domain, "__module__", "").startswith("sphinx.")):
                    # the domain doesn't yet support the new interface
                    log_warning(
                        f"Domain '{domain.__module__}::{domain.name}' has not "
                        "implemented a `resolve_any_xref` method",
                        subtype=MystWarnings.LEGACY_DOMAIN,
                        location=None,
                        once=True,
                    )

        # warn if we have more than one result
        if len(results) > 1:

            def stringify(name, node):
                reftitle = node.get("reftitle", node.astext())
                return f":{name}:`{reftitle}`"

            candidates = " or ".join(stringify(name, role) for name, role in results)
            log_warning(
                f"more than one target found for {target!r}: could be {candidates}",
                location=node,
                subtype=MystWarnings.XREF_DUPLICATE,
            )

        newnode: None | Element = None
        res_role: None | str = None
        if results:
            res_role, newnode = results[0]

        if newnode is None and ref_domains is None:
            newnode = env.app.emit_firstresult(
                "missing-reference",
                env,
                node,
                contnode,
                allowed_exceptions=(NoUri,),
            )

        # replace node children with the original nodes, if they were explicitly set
        if newnode and node["refexplicit"]:
            newnode.children = [contnode]

        if newnode and res_role:
            # Add classes to the node's first child, for styling
            res_domain = res_role.split(":")[0]
            if len(newnode) > 0 and isinstance(newnode[0], nodes.Element):
                _classes = newnode[0].get("classes", [])
                with suppress(ValueError):
                    _classes.remove("xref")
                if res_domain not in _classes:
                    _classes.append(res_domain)
                if res_role.replace(":", "-") not in _classes:
                    _classes.append(res_role.replace(":", "-"))
                newnode[0]["classes"] = _classes

        # create warnings
        if newnode is None:
            log_warning(
                f"no target found for {target!r}"
                + ("" if ref_domains is None else f" in domains {ref_domains}"),
                location=node,
                subtype=MystWarnings.XREF_MISSING,
            )
        elif not newnode.astext():
            log_warning(
                f"empty link text for target {target!r}"
                + (f" ({res_role})" if res_role else ""),
                location=node,
                subtype=MystWarnings.XREF_EMPTY,
            )

        return newnode


def resolve_intersphinx(
    env: BuildEnvironment,
    node: Element,
    contnode: Element,
    inv_name: None | str,
    domain_name: None | str,
    typ: None | str,
) -> None | tuple[str, str, Element]:
    """Resolve a cross-reference to an intersphinx inventory.

    This mirrors `sphinx.ext.intersphinx._resolve_reference` (available from sphinx 4.3)
    but adds additional features:

    - allows for missing object typ, this will then search all types in the domain
    - warn on matches in multiple inventories/domains

    :param env: The sphinx build environment
    :param node: The pending xref node, this requires the `reftarget` attribute,
        and the 'refexplicit' attribute is optional
    :param contnode: The content node, this is the node that will be used to
        display the link text
    :param inv_name: The name of the intersphinx inventory to use, if None then
        all inventories will be searched
    :param domain_name: The name of the domain to search, if None then all domains
        will be searched
    :param typ: The type of object to search for, if None then all types will be searched

    :returns: tuple of (inv_name, domain_name, resolved node),
        or None if no match was found
    """
    # TODO upstream this to sphinx?

    try:
        from sphinx.ext.intersphinx import (
            InventoryAdapter,
            _resolve_reference_in_domain,
        )
    except ImportError:
        log_warning(
            "Sphinx >= 4.3 is required",
            subtype=MystWarnings.XREF_ERROR,
            location=node,
        )
        return None

    inv_lookup = InventoryAdapter(env)
    if inv_name is None:
        inventories = inv_lookup.named_inventory
    else:
        if inv_name not in inv_lookup.named_inventory:
            log_warning(
                f"Unknown inventory {inv_name!r}",
                location=node,
                subtype=MystWarnings.IREF_MISSING,
            )
            return None
        inventories = {inv_name: inv_lookup.named_inventory[inv_name]}

    # get domains to search
    if domain_name is None:
        # search all domains
        domains = list(env.domains.values())
    else:
        if domain_name not in env.domains:
            # TODO create warning
            return None
        domains = [env.domains[domain_name]]

    # search over domains and inventories
    results = []
    for (_inv_name, inventory), domain in product(inventories.items(), domains):
        # object types to search for
        obj_types: list[str]
        if typ is None:
            # search all types
            obj_types = list(domain.object_types)
        else:
            obj_types = domain.objtypes_for_role(typ)

        if not obj_types:
            continue

        # TODO ideally we would warn if multiple results found for different types,
        # but currently this function just returns the first match
        res = _resolve_reference_in_domain(
            env, _inv_name, inventory, False, domain, obj_types, node, contnode
        )
        if res:
            results.append((_inv_name, domain.name, res))

    # warn if we have none or more than one result
    loc = ":".join([inv_name or "?", domain_name or "?", typ or "?", node["reftarget"]])

    if not results:
        log_warning(
            f"Unmatched target {loc!r}",
            location=node,
            subtype=MystWarnings.IREF_MISSING,
        )
        return None

    if len(results) > 1:
        matches = ",".join([f"'{i}:{d}'" for i, d, _ in results])
        log_warning(
            f"Multiple matches found for target {loc!r} in {matches}",
            location=node,
            subtype=MystWarnings.IREF_DUPLICATE,
        )

    res_inv, res_domain, res_node = results[0]
    # add a class, so we can capture what the match was in the output
    res_node["classes"].append(f"inv-{res_inv}-{res_domain}-{typ or ''}")

    return res_node
