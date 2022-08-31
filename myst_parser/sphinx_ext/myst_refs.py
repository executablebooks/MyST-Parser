"""A post-transform for overriding the behaviour of sphinx reference resolution.

This is applied to MyST type references only, such as ``[text](target)``,
and allows for nested syntax
"""
from __future__ import annotations

from contextlib import contextmanager, suppress
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


@contextmanager
def tmp_node_attrs(node: Element, **attrs: dict):
    """Temporarily set node attributes."""
    old_attrs = {key: node[key] for key in attrs if key in node}
    for key, val in attrs.items():
        node[key] = val
    yield
    for key in attrs:
        if key in old_attrs:
            node[key] = old_attrs[key]
        elif key in node:
            del node[key]


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
        elif typ == "external":
            newnode = self._resolve_xref_external(
                env, fromdocname, builder, node, contnode
            )
        else:
            log_warning(
                f"Unknown reference type {typ!r}",
                location=node,
                subtype=MystWarnings.REF_TYPE,
            )
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
                subtype=MystWarnings.REF_MISSING,
            )
            return None
        if node["refexplicit"]:
            # replace children of the new node with those of the contnode
            # and make classes similar to those produced by `std:ref` role
            with suppress(ValueError):
                contnode["classes"].remove("xref")
            contnode["classes"].extend(["std", "std-ref"])
            newnode.children = [contnode]

        if newnode and node.get("title"):
            newnode["reftitle"] = node["title"]

        return newnode

    def _resolve_xref_external(
        self,
        env: BuildEnvironment,
        fromdocname: str,
        builder: Builder,
        node: pending_xref,
        contnode: Element,
    ) -> Element | None:
        """Resolve a cross-reference to an external project."""
        from sphinx.ext.intersphinx import (
            inventory_exists,
            resolve_reference_any_inventory,
            resolve_reference_in_inventory,
        )

        refquery = node.get("refquery", {})
        inv_name = refquery.get("inv")
        if not inventory_exists(env, inv_name):
            log_warning(
                f"Unknown external reference inventory {inv_name!r}",
                location=node,
                subtype=MystWarnings.REF_MISSING,
            )
            return None
        with tmp_node_attrs(
            node,
            reftype=refquery.get("type", "any"),
            refdomain=refquery.get("domain", "std"),
        ):
            if inv_name is not None:
                newnode = resolve_reference_in_inventory(env, inv_name, node, contnode)
            else:
                newnode = resolve_reference_any_inventory(env, False, node, contnode)
        if not newnode:
            loc = [
                inv_name or "any",
                refquery.get("domain", "-"),
                refquery.get("type", "any"),
            ]
            log_warning(
                f"Unknown external reference {node['reftarget']!r} in '{':'.join(loc)}'",
                location=node,
                subtype=MystWarnings.REF_MISSING,
            )
            return None
        if newnode and node.get("title"):
            newnode["reftitle"] = node["title"]
        # TODO
        # if not node["refexplicit"] and not newnode.astext():
        #     newnode.insert(0, nodes.Text(" "))
        return newnode

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
                subtype=MystWarnings.REF_MISSING,
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
                    subtype=MystWarnings.REF_MISSING,
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
                        subtype=MystWarnings.REF_EMPTY,
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
                subtype=MystWarnings.REF_DUPLICATE,
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

        if newnode and node.get("title"):
            newnode["reftitle"] = node["title"]

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
                subtype=MystWarnings.REF_MISSING,
            )
        elif not newnode.astext():
            log_warning(
                f"empty link text for target {target!r}"
                + (f" ({res_role})" if res_role else ""),
                location=node,
                subtype=MystWarnings.REF_EMPTY,
            )

        return newnode
