"""Handle bibliographies."""
from pathlib import Path
from typing import Dict, List

import yaml
from docutils import nodes
from docutils.transforms import Transform
from markdown_it import MarkdownIt
from markdown_it.rules_inline import StateInline

# TODO sphinx.domain.citation CitationDefinitionTransform & CitationReferenceTransform
# does something a bit odd, and not the same as base docutils: it uses the
# label.astext() of the definition and reference.astext() to create target/ref ids,
# rather than the refname set on the reference, or the name set on the definition.
# this essentially means that you cannot have a reference/definition id,
# which is different to the label, e.g. ref [1] pointing to [abc] definition

# in converting the citation_reference to a pending_xref, it also
# discards the citation_reference's attributes (except ids/classes) and children

# when going back to a reference node
# (in sphinx.transforms.post_transforms.ReferencesResolver)
# the ids and classes also are propogated to the reference node


# TODO the implementation here simply adds a bibliography per document,
# de-duplicating the ref keys per document.
# But it might be the case that you want a single bibliography for all documents.

# TODO reference label formating e.g. [@key "{author}"],
# default would be [@key "[{label_}]"]
# (label_ would be a special key, matching definition label format)
# and definition formatting in config e.g. --myst-bib-format="{author} {year}"
# TODO a problem in docutils,
# is that the containing braces [] are added in the HTMLTranslator
# also in LaTeXTranslator (and there one should use --figure-citations)


def bibliography_plugin(md: MarkdownIt):
    """Register bibliography plugin."""
    md.inline.ruler.after("image", "bibliography_ref", bibliography_ref)
    md.add_render_rule("bibliography_ref", render_bibliography_ref)


def render_bibliography_ref(self, tokens, idx, options, env):
    # should be transformed
    return ""


def bibliography_ref(state: StateInline, silent: bool):
    """Process bibliography references ([@...])"""
    # mirrors markdown-it-footnote footnote_ref

    maximum = state.posMax
    start = state.pos

    # should be at least 4 chars - "[@x]"
    if start + 3 > maximum:
        return False

    if state.srcCharCode[start] != 0x5B:  # /* [ */
        return False
    if state.srcCharCode[start + 1] != 0x40:  # /* @ */
        return False

    pos = start + 2
    escaped = False
    while pos < maximum:
        if state.srcCharCode[pos] == 0x5C:  # /* \ */
            escaped = True
        elif not escaped and state.srcCharCode[pos] == 0x5D:  # /* ] */
            break
        else:
            escaped = False
        pos += 1

    if pos == start + 2:  # no empty bibliography labels
        return False
    if pos >= maximum:
        return False
    pos += 1

    if not silent:
        key_format = state.src[start + 2 : pos - 1].split(maxsplit=1)
        key = key_format[0]
        fmt = key_format[1] if len(key_format) > 1 else None
        token = state.push("bibliography_ref", "", 0)
        token.meta = {"key": key, "format": fmt}

    state.pos = pos
    state.posMax = maximum
    return True


class MystBibliographyTransform(Transform):
    """Transform for bibliographies."""

    default_priority = 10  # TODO suitable priority

    @property
    def sphinx_env(self):
        """Return the sphinx env, if using Sphinx."""
        try:
            return self.document.settings.env
        except AttributeError:
            return None

    def report_warning(self, message: str, subtype: str, node: nodes.Node):
        """Report warning."""
        message = f"{message} [myst.{subtype}]"
        if self.sphinx_env:
            from sphinx.util import logging

            logger = logging.getLogger(__name__)
            logger.warning(message, type="myst", subtype="bib", location=node)
        else:
            self.document.reporter.warning(message, base_node=node)

    def apply(self):
        """Apply the transform."""

        # find all bibliography references in the document
        citation_keys: Dict[str, List[nodes.reference]] = {}
        # findall is only in docutils >= 0.18
        iterator = (
            self.document.iterall
            if hasattr(self.document, "iterall")
            else self.document.traverse
        )
        for node in iterator(nodes.reference):
            if "myst-bib-ref" not in node.attributes.get("classes", ()):
                continue
            citation_keys.setdefault(node["key"], []).append(node)

        # nothing to do
        if not citation_keys:
            return

        # read bibliographies
        # TODO you would want to cache this in sphinx
        bib_definitions: Dict[str, dict] = {}
        for bibliography in getattr(self.document.settings, "myst_bib_files", []):
            # TODO handle read errors
            # TODO you would also want to set these paths as dependencies
            if self.sphinx_env:
                # bibliography paths should be relative to the source directory
                path = Path(self.sphinx_env.app.srcdir) / bibliography
            else:
                path = Path(bibliography)
            bib_bytes = path.read_bytes()
            # this ensures that the parent file is rebuilt if the included file changes
            self.document.settings.record_dependencies.add(str(path))
            # TODO here we would want to allow a different parser (via entry-point?),
            # based on the file extension
            # parser = parsers[path.suffix]
            parser = lambda b: yaml.load(  # noqa
                b.decode("utf8"), Loader=yaml.SafeLoader
            )
            bib_data = parser(bib_bytes)
            # TODO check read format, handle clashes
            for key, data in bib_data.items():
                if key not in bib_definitions:
                    bib_definitions[key] = {"path": path, "data": data}
                else:
                    pass  # TODO handle key clashes

        # Format bibliography references
        # note since python 3.7 dict insertion order is guaranteed
        for index, (key, references) in enumerate(citation_keys.items(), start=1):
            if key not in bib_definitions:
                # report and replace
                for refnode in references:
                    self.report_warning(
                        f"Bibliographic key {key!r} not found",
                        subtype="bib",
                        node=refnode,
                    )
                    refnode.replace_self(nodes.inline(f"[{key}]", f"[{key}]"))
                continue

            refname = f"myst-bib-{key}"
            definition_data = bib_definitions[key]

            # update reference nodes
            for refnode in references:
                refnode["refname"] = refname
                self.document.note_refname(refnode)
                refnode += nodes.Text(f"[{index}]")

            # add definition nodes
            # TODO these are currently added to the bottom of the document,
            # but what about ordering of citations vs footnotes
            # also do we want to add a (configured) heading/rubric
            # or let the user decide where they are placed

            # definition_node = nodes.paragraph(bib_file=str(definition_data["path"]))
            # definition_node.source = self.document["source"]
            # self.document += definition_node
            # label_node = nodes.label("", refname)
            # definition_node += label_node
            # label_node["names"].append(refname)
            # self.document.note_explicit_target(label_node, label_node)

            bib_list = nodes.definition_list(classes=["simple", "myst-bib-defs"])
            bib_list.source = self.document["source"]
            self.document += bib_list
            item = nodes.definition_list_item()
            bib_list += item
            term = nodes.term()
            item += term
            # TODO use https://docs.python.org/3/library/stdtypes.html#str.format_map
            label_node = nodes.inline("", f"[{key}]")
            label_node["names"].append(refname)
            self.document.note_explicit_target(label_node, label_node)
            term += label_node
            definition = nodes.definition()
            item += definition
            para = nodes.paragraph()
            definition += para
            para += nodes.Text(f"{definition_data['path']}")
