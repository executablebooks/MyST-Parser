"""A post-transform for overriding the behaviour of sphinx reference resolution.

This is applied to MyST type references only, such as ``[text](target)``,
and allows for nested syntax
"""
from __future__ import annotations

import re
from contextlib import suppress
from typing import TYPE_CHECKING, cast

from docutils import nodes
from docutils.nodes import Element
from sphinx.addnodes import pending_xref
from sphinx.domains import Domain
from sphinx.domains.std import StandardDomain
from sphinx.errors import NoUri
from sphinx.ext.intersphinx import InventoryAdapter
from sphinx.locale import _
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
    # TODO bypass reference warnings on nitpicky?
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
        ref_query = node.get("refquery", {})
        ref_inv = ref_query.get("name")
        ref_domain = ref_query.get("domain")
        ref_type = ref_query.get("type")
        ref_target = node["reftarget"]
        ref_regex = "regex" in ref_query

        res = resolve_intersphinx(
            env, node, ref_inv, ref_domain, ref_type, ref_target, ref_regex
        )

        if res is None:
            return None

        # create a new node
        res_inv, res_domain, res_type, res_target, (proj, version, uri, dispname) = res

        if node.get("title"):
            reftitle = node["title"]
        elif version:
            reftitle = _("(in %s v%s)") % (proj, version)
        else:
            reftitle = _("(in %s)") % (proj,)

        res_node = nodes.reference(
            "", "", internal=False, refuri=uri, reftitle=reftitle
        )
        # add a class, so we can capture what the match was in the output
        res_node["classes"].append(f"inv-{res_inv}-{res_domain}-{res_type}")
        if node.get("refexplicit"):
            res_node.append(contnode)
        elif dispname == "-":
            res_node.append(nodes.literal(res_target, res_target))
        else:
            res_node.append(nodes.Text(dispname))

        return res_node

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
    ref_inv: None | str,
    ref_domain: None | str,
    ref_type: None | str,
    ref_target: str,
    regex_match=False,
) -> None | tuple[str, str, str, str, tuple[str, str, str, str]]:
    """Resolve a cross-reference to an intersphinx inventory.

    This mirrors `sphinx.ext.intersphinx._resolve_reference` (available from sphinx 4.3)
    but adds additional features:

    - allows for missing object typ, this will then search all types in the domain
    - warn on matches in multiple inventories/domains

    :param env: The sphinx build environment
    :param node: The pending xref node, used for logging location
    :param ref_inv: The name of the intersphinx inventory to use, if None then
        all inventories will be searched
    :param ref_domain: The name of the domain to search, if None then all domains
        will be searched
    :param ref_type: The type of object to search for, if None then all types will be searched
    :param ref_target: The target to search for
    :param regex_match: Whether to use regex matching of the target

    :returns: resolved data, or None if not found
    """
    inventories = InventoryAdapter(env).named_inventory

    if regex_match:
        ref_target_re = re.compile(ref_target)
    else:
        ref_target_re = None

    # get the inventories to search
    if ref_inv is not None and ref_inv not in inventories:
        log_warning(
            f"Unknown inventory {ref_inv!r}",
            location=node,
            subtype=MystWarnings.IREF_MISSING,
        )
        return None
    elif ref_inv is not None:
        inventories = {ref_inv: inventories[ref_inv]}

    # search through the inventories
    results = []
    for inv_name, inv_data in inventories.items():

        for domain_obj_name, data in inv_data.items():

            domain_name, obj_type = domain_obj_name.split(":", 1)

            if ref_domain is not None and ref_domain != domain_name:
                continue

            if ref_type is not None and ref_type != obj_type:
                continue

            if not regex_match and ref_target in data:
                results.append(
                    (inv_name, domain_name, obj_type, ref_target, data[ref_target])
                )
            elif ref_target_re is not None:
                for target in data:
                    if ref_target_re.fullmatch(target):
                        results.append(
                            (inv_name, domain_name, obj_type, target, data[target])
                        )

    # warn if we have none or more than one result
    loc = ":".join([ref_inv or "?", ref_domain or "?", ref_type or "?", ref_target])

    if not results:
        log_warning(
            f"Unmatched target {loc!r}",
            location=node,
            subtype=MystWarnings.IREF_MISSING,
        )
        return None

    if len(results) > 1:
        matches = [f"'{i}:{d}:{o}:{t}'" for i, d, o, t, _ in results]
        if len(matches) > 4:
            matches = matches[:5] + ["..."]
        log_warning(
            f"Multiple matches found for target {loc!r} in {','.join(matches)}",
            location=node,
            subtype=MystWarnings.IREF_DUPLICATE,
        )

    return results[0]
