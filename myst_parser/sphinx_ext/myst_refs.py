"""A post-transform for overriding the behaviour of sphinx reference resolution.

This is applied to MyST type references only, such as ``[text](target)``,
and allows for nested syntax
"""
import re
from typing import Any, List, Optional, Tuple, cast

from docutils import nodes
from docutils.nodes import Element, document
from sphinx import addnodes
from sphinx.addnodes import pending_xref
from sphinx.domains.std import StandardDomain
from sphinx.errors import NoUri
from sphinx.locale import __
from sphinx.transforms.post_transforms import ReferencesResolver
from sphinx.util import docname_join, logging
from sphinx.util.nodes import clean_astext, make_refnode

from myst_parser._compat import findall
from myst_parser.warnings_ import MystWarnings

LOGGER = logging.getLogger(__name__)


def log_warning(msg: str, subtype: MystWarnings, **kwargs: Any):
    """Log a warning, with a myst type and specific subtype."""
    LOGGER.warning(
        msg + f" [myst.{subtype.value}]", type="myst", subtype=subtype.value, **kwargs
    )


class MystReferenceResolver(ReferencesResolver):
    """Resolves cross-references on doctrees.

    Overrides default sphinx implementation, to allow for nested syntax
    """

    default_priority = 9  # higher priority than ReferencesResolver (10)

    def run(self, **kwargs: Any) -> None:
        self.document: document
        for node in findall(self.document)(addnodes.pending_xref):
            if node["reftype"] != "myst":
                continue

            if node["refdomain"] == "doc":
                self.resolve_myst_ref_doc(node)
                continue

            contnode = cast(nodes.TextElement, node[0].deepcopy())
            newnode = None

            target = node["reftarget"]
            refdoc = node.get("refdoc", self.env.docname)

            try:
                newnode = self.resolve_myst_ref_any(refdoc, node, contnode)
                if newnode is None:
                    # no new node found? try the missing-reference event
                    # but first we change the the reftype to 'any'
                    # this means it is picked up by extensions like intersphinx
                    node["reftype"] = "any"
                    try:
                        newnode = self.app.emit_firstresult(
                            "missing-reference",
                            self.env,
                            node,
                            contnode,
                            allowed_exceptions=(NoUri,),
                        )
                    finally:
                        node["reftype"] = "myst"
                    if newnode is None:
                        # still not found? warn if node wishes to be warned about or
                        # we are in nit-picky mode
                        self._warn_missing_reference(target, node)
            except NoUri:
                newnode = contnode

            if not newnode:
                newnode = nodes.reference()
                newnode["refid"] = target
                newnode.append(node[0].deepcopy())

            if (
                len(newnode.children) == 1
                and isinstance(newnode[0], nodes.inline)
                and not (newnode[0].children)
            ):
                newnode[0].replace_self(nodes.literal(target, target))
            elif not newnode.children:
                newnode.append(nodes.literal(target, target))

            node.replace_self(newnode)

    def _warn_missing_reference(self, target: str, node: pending_xref) -> None:
        """Warn about a missing reference."""
        dtype = "myst"
        if not node.get("refwarn"):
            return
        if (
            self.config.nitpicky
            and self.config.nitpick_ignore
            and (dtype, target) in self.config.nitpick_ignore
        ):
            return
        if (
            self.config.nitpicky
            and self.config.nitpick_ignore_regex
            and any(
                (
                    re.fullmatch(ignore_type, dtype)
                    and re.fullmatch(ignore_target, target)
                )
                for ignore_type, ignore_target in self.config.nitpick_ignore_regex
            )
        ):
            return

        log_warning(
            f"'myst' cross-reference target not found: {target!r}",
            MystWarnings.XREF_MISSING,
            location=node,
        )

    def resolve_myst_ref_doc(self, node: pending_xref):
        """Resolve a reference, from a markdown link, to another document,
        optionally with a target id within that document.
        """
        from_docname = node.get("refdoc", self.env.docname)
        ref_docname: str = node["reftarget"]
        ref_id: Optional[str] = node["reftargetid"]

        if ref_docname not in self.env.all_docs:
            log_warning(
                f"Unknown source document {ref_docname!r}",
                MystWarnings.XREF_MISSING,
                location=node,
            )
            node.replace_self(node[0].deepcopy())
            return

        targetid = ""
        implicit_text = ""
        inner_classes = ["std", "std-doc"]

        if ref_id:
            slug_to_section = self.env.metadata[ref_docname].get("myst_slugs", {})
            if ref_id not in slug_to_section:
                log_warning(
                    f"local id not found in doc {ref_docname!r}: {ref_id!r}",
                    MystWarnings.XREF_MISSING,
                    location=node,
                )
                targetid = ref_id
            else:
                _, targetid, implicit_text = slug_to_section[ref_id]
            inner_classes = ["std", "std-ref"]
        else:
            implicit_text = clean_astext(self.env.titles[ref_docname])

        if node["refexplicit"]:
            caption = node.astext()
            innernode = nodes.inline(caption, "", classes=inner_classes)
            innernode.extend(node[0].children)
        else:
            innernode = nodes.inline(
                implicit_text, implicit_text, classes=inner_classes
            )

        assert self.app.builder
        ref_node = make_refnode(
            self.app.builder, from_docname, ref_docname, targetid, innernode
        )
        node.replace_self(ref_node)

    def resolve_myst_ref_any(
        self, refdoc: str, node: pending_xref, contnode: Element
    ) -> Element:
        """Resolve reference generated by the "myst" role; ``[text](reference)``.

        This builds on the sphinx ``any`` role to also resolve:

        - Document references with extensions; ``[text](./doc.md)``
        - Document references with anchors with anchors; ``[text](./doc.md#target)``
        - Nested syntax for explicit text with std:doc and std:ref;
          ``[**nested**](reference)``

        """
        target: str = node["reftarget"]
        results: List[Tuple[str, Element]] = []

        # resolve standard references
        res = self._resolve_ref_nested(node, refdoc)
        if res:
            results.append(("std:ref", res))

        # resolve doc names
        res = self._resolve_doc_nested(node, refdoc)
        if res:
            results.append(("std:doc", res))

        # get allowed domains for referencing
        ref_domains = self.env.config.myst_ref_domains

        assert self.app.builder

        # next resolve for any other standard reference objects
        if ref_domains is None or "std" in ref_domains:
            stddomain = cast(StandardDomain, self.env.get_domain("std"))
            for objtype in stddomain.object_types:
                key = (objtype, target)
                if objtype == "term":
                    key = (objtype, target.lower())
                if key in stddomain.objects:
                    docname, labelid = stddomain.objects[key]
                    domain_role = "std:" + stddomain.role_for_objtype(objtype)
                    ref_node = make_refnode(
                        self.app.builder, refdoc, docname, labelid, contnode
                    )
                    results.append((domain_role, ref_node))

        # finally resolve for any other type of allowed reference domain
        for domain in self.env.domains.values():
            if domain.name == "std":
                continue  # we did this one already
            if ref_domains is not None and domain.name not in ref_domains:
                continue
            try:
                results.extend(
                    domain.resolve_any_xref(
                        self.env, refdoc, self.app.builder, target, node, contnode
                    )
                )
            except NotImplementedError:
                # the domain doesn't yet support the new interface
                # we have to manually collect possible references (SLOW)
                if not (getattr(domain, "__module__", "").startswith("sphinx.")):
                    log_warning(
                        f"Domain '{domain.__module__}::{domain.name}' has not "
                        "implemented a `resolve_any_xref` method",
                        MystWarnings.LEGACY_DOMAIN,
                        once=True,
                    )
                for role in domain.roles:
                    res = domain.resolve_xref(
                        self.env, refdoc, self.app.builder, role, target, node, contnode
                    )
                    if res and len(res) and isinstance(res[0], nodes.Element):
                        results.append((f"{domain.name}:{role}", res))

        # now, see how many matches we got...
        if not results:
            return None
        if len(results) > 1:

            def stringify(name, node):
                reftitle = node.get("reftitle", node.astext())
                return f":{name}:`{reftitle}`"

            candidates = " or ".join(stringify(name, role) for name, role in results)
            log_warning(
                __(
                    f"more than one target found for 'myst' cross-reference {target}: "
                    f"could be {candidates}"
                ),
                MystWarnings.XREF_AMBIGUOUS,
                location=node,
            )

        res_role, newnode = results[0]
        # Override "myst" class with the actual role type to get the styling
        # approximately correct.
        res_domain = res_role.split(":")[0]
        if len(newnode) > 0 and isinstance(newnode[0], nodes.Element):
            newnode[0]["classes"] = newnode[0].get("classes", []) + [
                res_domain,
                res_role.replace(":", "-"),
            ]

        return newnode

    def _resolve_ref_nested(
        self, node: pending_xref, fromdocname: str, target=None
    ) -> Optional[Element]:
        """This is the same as ``sphinx.domains.std._resolve_ref_xref``,
        but allows for nested syntax, rather than converting the inner node to raw text.
        """
        stddomain = cast(StandardDomain, self.env.get_domain("std"))
        target = target or node["reftarget"].lower()

        if node["refexplicit"]:
            # reference to anonymous label; the reference uses
            # the supplied link caption
            docname, labelid = stddomain.anonlabels.get(target, ("", ""))
            sectname = node.astext()
            innernode = nodes.inline(sectname, "")
            innernode.extend(node[0].children)
        else:
            # reference to named label; the final node will
            # contain the section name after the label
            docname, labelid, sectname = stddomain.labels.get(target, ("", "", ""))
            innernode = nodes.inline(sectname, sectname)

        if not docname:
            return None

        assert self.app.builder
        return make_refnode(self.app.builder, fromdocname, docname, labelid, innernode)

    def _resolve_doc_nested(
        self, node: pending_xref, fromdocname: str
    ) -> Optional[Element]:
        """This is the same as ``sphinx.domains.std._resolve_doc_xref``,
        but allows for nested syntax, rather than converting the inner node to raw text.

        It also allows for extensions on document names.
        """
        docname = docname_join(node.get("refdoc", fromdocname), node["reftarget"])
        if docname not in self.env.all_docs:
            return None

        if node["refexplicit"]:
            # reference with explicit title
            caption = node.astext()
            innernode = nodes.inline(caption, "", classes=["doc"])
            innernode.extend(node[0].children)
        else:
            caption = clean_astext(self.env.titles[docname])
            innernode = nodes.inline(caption, caption, classes=["doc"])

        assert self.app.builder
        return make_refnode(self.app.builder, fromdocname, docname, "", innernode)
