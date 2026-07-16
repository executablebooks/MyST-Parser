"""Directives that can be applied to both Sphinx and docutils."""

from __future__ import annotations

import re
import typing as t

from docutils import nodes
from docutils.transforms import Transform
from docutils.transforms.references import Footnotes
from markdown_it.common.normalize_url import normalizeLink

from myst_parser._compat import findall
from myst_parser.mdit_to_docutils.base import clean_astext
from myst_parser.warnings_ import MystWarnings, create_warning


class UnreferencedFootnotesDetector(Transform):
    """Detect unreferenced footnotes and emit warnings.

    Replicates https://github.com/sphinx-doc/sphinx/pull/12730,
    but also allows for use in docutils (without sphinx).
    """

    default_priority = Footnotes.default_priority + 2

    # document: nodes.document

    def apply(self, **kwargs: t.Any) -> None:
        """Apply the transform."""

        for node in self.document.footnotes:
            # note we do not warn on duplicate footnotes here
            # (i.e. where the name has been moved to dupnames)
            # since this is already reported by docutils
            if not node["backrefs"] and node["names"]:
                create_warning(
                    self.document,
                    "Footnote [{}] is not referenced.".format(node["names"][0])
                    if node["names"]
                    else node["dupnames"][0],
                    wtype="ref",
                    subtype="footnote",
                    node=node,
                )
        for node in self.document.symbol_footnotes:
            if not node["backrefs"]:
                create_warning(
                    self.document,
                    "Footnote [*] is not referenced.",
                    wtype="ref",
                    subtype="footnote",
                    node=node,
                )
        for node in self.document.autofootnotes:
            # note we do not warn on duplicate footnotes here
            # (i.e. where the name has been moved to dupnames)
            # since this is already reported by docutils
            if not node["backrefs"] and node["names"]:
                create_warning(
                    self.document,
                    "Footnote [#] is not referenced.",
                    wtype="ref",
                    subtype="footnote",
                    node=node,
                )


class SortFootnotes(Transform):
    """Sort auto-numbered, labelled footnotes by the order they are referenced.

    This is run before the docutils ``Footnote`` transform, where numbered labels are assigned.
    """

    default_priority = Footnotes.default_priority - 2

    # document: nodes.document

    def apply(self, **kwargs: t.Any) -> None:
        """Apply the transform."""
        if not self.document.settings.myst_footnote_sort:
            return

        ref_order: list[str] = [
            node["refname"]
            for node in self.document.autofootnote_refs
            if "refname" in node
        ]

        def _sort_key(node: nodes.footnote) -> int:
            if node["names"] and node["names"][0] in ref_order:
                return ref_order.index(node["names"][0])
            return 999

        self.document.autofootnotes.sort(key=_sort_key)


class CollectFootnotes(Transform):
    """Transform to move footnotes to the end of the document, and sort by label."""

    default_priority = Footnotes.default_priority + 3

    # document: nodes.document

    def apply(self, **kwargs: t.Any) -> None:
        """Apply the transform."""
        if not self.document.settings.myst_footnote_sort:
            return

        footnotes: list[tuple[str, nodes.footnote]] = []
        for footnote in (
            self.document.symbol_footnotes
            + self.document.footnotes
            + self.document.autofootnotes
        ):
            label = footnote.children[0]
            footnotes.append((label.astext(), footnote))

        if (
            footnotes
            and self.document.settings.myst_footnote_transition
            # avoid warning: Document or section may not begin with a transition
            and not all(isinstance(c, nodes.footnote) for c in self.document.children)
        ):
            transition = nodes.transition(classes=["footnotes"])
            transition.source = self.document.source
            self.document += transition

        def _sort_key(footnote: tuple[str, nodes.footnote]) -> int | str:
            label, _ = footnote
            try:
                # ensure e.g 10 comes after 2
                return int(label)
            except ValueError:
                return label

        for _, footnote in sorted(footnotes, key=_sort_key):
            footnote.parent.remove(footnote)
            self.document += footnote


class AddSlugIds(Transform):
    """Emit each heading's anchor slug as an additional (secondary) id.

    This makes the anchor actually exist in published HTML output.

    It must run only after *all* other id assignment — docutils'
    ``PropagateTargets`` (260) and sphinx's ``SortIds`` (261) included —
    so that a slug can neither claim an id another element would otherwise
    receive, nor become a section's primary id: primary ids (used by
    tocs, permalinks and ``objects.inv``) are unchanged by this transform.
    Slugs are registered in ``document.ids`` directly (not via ``set_id``),
    deliberately bypassing ``id_prefix``: the raw slug is the anchor.
    """

    default_priority = 700  # after all id assignment, before ResolveAnchorIds

    def apply(self, **kwargs: t.Any) -> None:
        """Apply the transform."""
        if not getattr(self.document.settings, "myst_heading_anchors_html_ids", True):
            return
        for node in findall(self.document)(nodes.Element):
            slug = node.get("slug")
            if (
                slug
                # a custom slug_func may produce whitespace,
                # which is invalid in an HTML id
                and not re.search(r"\s", slug)
                and slug not in self.document.ids
            ):
                node["ids"].append(slug)
                self.document.ids[slug] = node


class PrioritiseExplicitIds(Transform):
    """Reorder ``section["ids"]`` so an explicitly named target's id is first.

    Docutils' ``PropagateTargets`` (priority 260) appends propagated target
    ids *after* the section's implicit id, so themes, tocs, permalinks and
    ``objects.inv`` pick up the (unstable) implicit id.  This moves the
    explicitly named id earliest in the id list (for multiple ``(name)=``
    targets, that is the one nearest the heading) to the front; the implicit
    id remains in the list, as a secondary anchor, so previously published
    fragments keep working.
    """

    # strictly after docutils' PropagateTargets (260) and sphinx's SortIds
    # (261), so the ordering does not depend on transform insertion order
    default_priority = 262

    def apply(self, **kwargs: t.Any) -> None:
        """Apply the transform."""
        explicit_ids = {
            self.document.nameids[name]
            for name, is_explicit in self.document.nametypes.items()
            if is_explicit and self.document.nameids.get(name)
        }
        for section in findall(self.document)(nodes.section):
            ids = section["ids"]
            first = next((id_ for id_ in ids if id_ in explicit_ids), None)
            if first is not None and ids[0] != first:
                ids.remove(first)
                ids.insert(0, first)


class ResolveAnchorIds(Transform):
    """Transform for resolving `[name](#id)` type links."""

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
                    if isinstance(subnode, nodes.caption | nodes.title):
                        implicit_title = clean_astext(subnode)
                        break
            if implicit_title is None:
                # handle definition lists and field lists
                if (
                    isinstance(node, nodes.definition_list | nodes.field_list)
                    and node.children
                ):
                    node = node[0]
                if (
                    isinstance(node, nodes.field | nodes.definition_list_item)
                    and node.children
                ):
                    node = node[0]
                if isinstance(node, nodes.term | nodes.field_name):
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

            # candidate implicit local anchor: covers e.g. headings not
            # assigned a slug (beyond the `heading_anchors` depth), whose
            # anchors nonetheless exist in the output
            labelid = self.document.nameids.get(target) or (
                target if target in self.document.ids else None
            )
            node = self.document.ids.get(labelid) if labelid else None
            if node is None or (
                node.tagname == "footnote"
                or "refuri" in node
                or node.tagname.startswith("desc_")
            ):
                labelid = None

            # in docutils (single-document) mode, resolve to the local
            # anchor directly (previously these links warned);
            # in sphinx mode it is only recorded on the pending_xref, as a
            # last-resort fallback after project-wide resolution, so that
            # the precedence of existing reference resolution is unchanged
            if labelid and not hasattr(self.document.settings, "env"):
                refnode["refid"] = labelid
                if not refnode.children:
                    implicit_title = None
                    for subnode in node or []:
                        if isinstance(subnode, nodes.caption | nodes.title):
                            implicit_title = clean_astext(subnode)
                            break
                    text = implicit_title or ("#" + target)
                    refnode += nodes.inline(text, text, classes=["std", "std-ref"])
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
                if labelid:
                    pending["reflocalid"] = labelid
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


def _child_sections(node: nodes.Element) -> list[nodes.section]:
    """Return the direct child sections of an element, in document order."""
    return [child for child in node.children if isinstance(child, nodes.section)]


def _number_sections(
    sections: list[nodes.section],
    prefix: tuple[int, ...],
    number_map: dict[tuple[int, ...], nodes.section],
) -> None:
    """Recursively assign structural numbers to sections, populating ``number_map``.

    The i-th (1-based) section at a level is numbered ``prefix + (i,)``, and the
    numbering recurses into each section's direct child sections.
    """
    for i, section in enumerate(sections, start=1):
        number = prefix + (i,)
        number_map[number] = section
        _number_sections(_child_sections(section), number, number_map)


def _leave_section_ref_inert(node: nodes.Element) -> bool:
    """Whether a section-reference marker (see ``render_section_ref``) should be left as inert styled text.

    A marker is left untouched (no link, no warning) when it sits inside:

    - a ``reference`` or ``pending_xref`` — converting it would nest an ``<a>``
      inside another ``<a>``, which is invalid HTML; or
    - a ``title`` — a reference here would be copied into navigation/toc entries
      (sphinx toctree entry links, docutils contents entries), again nesting
      ``<a>`` in those navs.
    """
    parent = node.parent
    while parent is not None:
        if (
            isinstance(parent, nodes.reference | nodes.title)
            or parent.tagname == "pending_xref"
        ):
            return True
        parent = parent.parent
    return False


class ResolveSectionRefs(Transform):
    """Resolve ``§1.1`` section references to the target section's anchor.

    Runs at priority 878, before ``ResolveAnchorIds`` (879) and before sphinx's
    ``DoctreeReadEvent`` (880), so that doctree-read consumers (``env.titles``,
    the toctree collector) see the resolved references rather than the raw
    markers.  By this point any doctitle promotion (320) has happened and every
    section id exists (docutils' ``PropagateTargets`` (260)/sphinx's ``SortIds``
    (261) and the later id transforms have all run).  Numbering is
    document-local and purely structural (independent of any ``:numbered:``
    toctree), so the same references resolve identically in docutils and sphinx.
    """

    default_priority = 878  # before ResolveAnchorIds (879)/DoctreeReadEvent (880)

    def apply(self, **kwargs: t.Any) -> None:
        """Apply the transform."""
        # gather the section-reference markers emitted by ``render_section_ref``;
        # these can only exist when the ``section_ref`` extension was enabled at
        # parse time, so their presence self-gates the transform
        markers = [
            node
            for node in findall(self.document)(nodes.inline)
            if "section_numbers" in node
        ]
        if not markers:
            return

        # build a document-local, structural map of section numbers to sections
        roots = _child_sections(self.document)
        # with a single top-level section (the common ``# Title`` layout, which
        # docutils doctitle promotion and sphinx local numbering both assume),
        # number its child sections; otherwise number the top-level sections
        top_sections = _child_sections(roots[0]) if len(roots) == 1 else roots
        number_map: dict[tuple[int, ...], nodes.section] = {}
        _number_sections(top_sections, (), number_map)

        for node in markers:
            # a reference nested inside a link or heading would produce invalid
            # nested anchors, so such markers are left as inert styled text
            if _leave_section_ref_inert(node):
                continue
            content = node.astext()
            number = tuple(node["section_numbers"])
            section = number_map.get(number)
            if section is not None and section["ids"]:
                ref = nodes.reference(
                    "",
                    "",
                    internal=True,
                    refid=section["ids"][0],
                    classes=["section-ref"],
                )
                ref += node.children
                # add the target's title as a hover tooltip (``title="..."`` in
                # sphinx HTML); the section's first child is its ``title``
                title_node = next(
                    (
                        child
                        for child in section.children
                        if isinstance(child, nodes.title)
                    ),
                    None,
                )
                if title_node is not None:
                    ref["reftitle"] = clean_astext(title_node)
                node.parent.replace(node, ref)
            else:
                create_warning(
                    self.document,
                    f"Section reference target not found: {content!r}",
                    MystWarnings.SECTION_REF,
                    line=node.line,
                )
