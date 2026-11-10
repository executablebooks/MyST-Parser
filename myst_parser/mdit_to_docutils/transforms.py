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

        footnotes: list[tuple[str | None, nodes.footnote]] = []
        for footnote in (
            self.document.symbol_footnotes
            + self.document.footnotes
            + self.document.autofootnotes
        ):
            # labels are assigned by docutils' ``Footnotes`` transform, which has not run
            # when the content is parsed into a sub-document (``.. include:: :parser:``),
            # so the first child may be a body element, or absent for an empty definition
            first = footnote.children[0] if footnote.children else None
            label = first.astext() if isinstance(first, nodes.label) else None
            footnotes.append((label, footnote))

        if (
            footnotes
            and self.document.settings.myst_footnote_transition
            # avoid warning: Document or section may not begin with a transition
            and not all(isinstance(c, nodes.footnote) for c in self.document.children)
        ):
            transition = nodes.transition(classes=["footnotes"])
            transition.source = self.document.source
            self.document += transition

        def _sort_key(
            footnote: tuple[str | None, nodes.footnote],
        ) -> tuple[int, int, str]:
            label, _ = footnote
            if label is None:
                # unlabelled: after all labelled footnotes; the sort is stable,
                # so they keep the order they are first referenced
                # (the order docutils numbers them)
                return (2, 0, "")
            try:
                # ensure e.g 10 comes after 2
                return (0, int(label), "")
            except ValueError:
                # non-numeric labels sort after numeric ones;
                # the leading discriminant keeps the key totally ordered,
                # since int and str cannot be compared with each other
                return (1, 0, label)

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
        explicit: dict[str, tuple[str, str | None]] = {}
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
                if "reftitle" in refnode:
                    pending["reftitle"] = refnode["reftitle"]
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


def _section_number_map(
    document: nodes.document,
) -> dict[tuple[int, ...], nodes.section]:
    """Map structural section numbers to their sections.

    The numbering is that of the document's heading hierarchy as written:
    when there is a single top-level heading (the common ``# Title`` layout),
    its child sections are numbered ``1``, ``2``, ...; otherwise the
    top-level sections themselves are.
    """
    number_map: dict[tuple[int, ...], nodes.section] = {}
    roots = _child_sections(document)
    if len(roots) == 1:
        _number_sections(_child_sections(roots[0]), (), number_map)
    else:
        _number_sections(roots, (), number_map)
    return number_map


def _leave_section_ref_inert(node: nodes.Element) -> bool:
    """Whether a section-reference marker (see ``render_section_ref``) should be left as inert styled text.

    A marker is left untouched (no link, no warning) when it sits inside:

    - a ``reference`` or ``pending_xref`` — converting it would nest an ``<a>``
      inside another ``<a>``, which is invalid HTML; or
    - a section heading — a reference there would be copied into navigation
      and toc entries (sphinx toctree entry links, docutils contents entries),
      again nesting ``<a>`` in those navs.

    Other titles (admonition, table, topic or sidebar titles) are not copied
    into navigation, so references in them are resolved as usual.
    """
    parent = node.parent
    while parent is not None:
        if (
            isinstance(parent, nodes.reference)
            or parent.tagname == "pending_xref"
            or (
                isinstance(parent, nodes.title)
                and isinstance(parent.parent, nodes.section)
            )
        ):
            return True
        parent = parent.parent
    return False


class ResolveSectionRefs(Transform):
    """Resolve ``§1.1`` section references to the target section's anchor.

    Numbering is document-local and purely structural (independent of any
    ``:numbered:`` toctree), see ``_section_number_map``.

    The transform runs on the headings as written, so the same references
    resolve identically in docutils and sphinx: after the id transforms, so
    each section's first id is final, and before docutils' doctitle and
    section-subtitle promotion, which sphinx never applies.
    A link to a heading that docutils later promotes to the subtitle still
    lands, because the promotion copies the section's ids onto the subtitle.
    """

    # strictly after docutils' PropagateTargets (260), sphinx's SortIds (261)
    # and PrioritiseExplicitIds (262), which settle each section's first id
    # (AddSlugIds (700) only appends), and strictly before docutils' DocTitle
    # (320) and SectSubTitle (350), which reshape the section tree;
    # this is also before sphinx's DoctreeReadEvent (880), so doctree-read
    # consumers (``env.titles``, the toctree collector) see the resolved
    # references rather than the raw markers
    default_priority = 300

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

        number_map = _section_number_map(self.document)

        for node in markers:
            # a reference nested inside a link or heading would produce invalid
            # nested anchors, so such markers are left as inert styled text
            if _leave_section_ref_inert(node):
                continue
            content = node.astext()
            number = tuple(node["section_numbers"])
            target = number_map.get(number)
            if target is not None and target["ids"]:
                ref = nodes.reference(
                    "",
                    "",
                    internal=True,
                    refid=target["ids"][0],
                    classes=["section-ref"],
                )
                ref += node.children
                # add the section title as a hover tooltip (``title="..."`` in
                # sphinx HTML)
                title_node = next(
                    (
                        child
                        for child in target.children
                        if isinstance(child, nodes.title)
                    ),
                    None,
                )
                if title_node is not None:
                    ref["reftitle"] = clean_astext(title_node)
                node.parent.replace(node, ref)
            else:
                # ``node=`` (not ``line=``) so the location is the file the
                # reference was written in, which differs inside an ``{include}``
                create_warning(
                    self.document,
                    f"Section reference target not found: {content!r}",
                    MystWarnings.SECTION_REF,
                    node=node,
                )
