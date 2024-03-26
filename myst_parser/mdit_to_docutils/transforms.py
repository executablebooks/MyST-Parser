"""Directives that can be applied to both Sphinx and docutils."""
from __future__ import annotations

import typing as t

from docutils import nodes
from docutils.transforms import Transform
from markdown_it.common.normalize_url import normalizeLink

from myst_parser._compat import findall
from myst_parser.mdit_to_docutils.base import clean_astext
from myst_parser.warnings_ import MystWarnings, create_warning


class ResolveAnchorIds(Transform):
    """Directive for resolving `[name](#id)` type links."""

    default_priority = 879  # this is the same as Sphinx's StandardDomain.process_doc

    def apply(self, **kwargs: t.Any) -> None:
        """Apply the transform."""
        # gather the implicit heading slugs
        # name -> (line, slug, title)
        slugs: dict[str, tuple[int, str, str]] = getattr(
            self.document, "myst_slugs", {}
        )

        # gather explicit references
        # this follows the same logic as Sphinx's StandardDomain.process_doc
        explicit: dict[str, tuple[str, None | str]] = {}
        for name, is_explicit in self.document.nametypes.items():
            if not is_explicit:
                continue
            labelid = self.document.nameids[name]
            if labelid is None:
                continue
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
                # ignore footnote labels, labels automatically generated from a
                # link and object descriptions
                continue

            implicit_title = None
            if node.tagname == "rubric":
                implicit_title = clean_astext(node)
            if implicit_title is None:
                # handle sections and and other captioned elements
                for subnode in node:
                    if isinstance(subnode, (nodes.caption, nodes.title)):
                        implicit_title = clean_astext(subnode)
                        break
            if implicit_title is None:
                # handle definition lists and field lists
                if (
                    isinstance(node, (nodes.definition_list, nodes.field_list))
                    and node.children
                ):
                    node = node[0]
                if (
                    isinstance(node, (nodes.field, nodes.definition_list_item))
                    and node.children
                ):
                    node = node[0]
                if isinstance(node, (nodes.term, nodes.field_name)):
                    implicit_title = clean_astext(node)

            explicit[name] = (labelid, implicit_title)

        for refnode in findall(self.document)(nodes.reference):
            if not refnode.get("id_link"):
                continue

            target = refnode["refuri"][1:]
            del refnode["refuri"]

            # search explicit first
            if target in explicit:
                ref_id, implicit_title = explicit[target]
                refnode["refid"] = ref_id
                if not refnode.children and implicit_title:
                    refnode += nodes.inline(
                        implicit_title, implicit_title, classes=["std", "std-ref"]
                    )
                elif not refnode.children:
                    refnode += nodes.inline(
                        "#" + target, "#" + target, classes=["std", "std-ref"]
                    )
                continue

            # now search implicit
            if target in slugs:
                _, sect_id, implicit_title = slugs[target]
                refnode["refid"] = sect_id
                if not refnode.children and implicit_title:
                    refnode += nodes.inline(
                        implicit_title, implicit_title, classes=["std", "std-ref"]
                    )
                continue

            # if still not found, and using sphinx, then create a pending_xref
            if hasattr(self.document.settings, "env"):
                from sphinx import addnodes

                pending = addnodes.pending_xref(
                    refdoc=self.document.settings.env.docname,
                    refdomain=None,
                    reftype="myst",
                    reftarget=target,
                    refexplicit=bool(refnode.children),
                )
                inner_node = nodes.inline(
                    "", "", classes=["xref", "myst"] + refnode["classes"]
                )
                for attr in ("ids", "names", "dupnames"):
                    inner_node[attr] = refnode[attr]
                inner_node += refnode.children
                pending += inner_node
                refnode.parent.replace(refnode, pending)
                continue

            # if still not found, and using docutils, then create a warning
            # and simply output as a url

            create_warning(
                self.document,
                f"'myst' reference target not found: {target!r}",
                MystWarnings.XREF_MISSING,
                line=refnode.line,
                append_to=refnode,
            )
            refnode["refid"] = normalizeLink(target)
            if not refnode.children:
                refnode += nodes.inline(
                    "#" + target, "#" + target, classes=["std", "std-ref"]
                )
