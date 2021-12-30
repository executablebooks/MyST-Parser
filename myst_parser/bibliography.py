"""Handle bibliographies."""
from pathlib import Path
from typing import Dict, List

import yaml
from docutils import nodes
from docutils.transforms import Transform

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

    def apply(self):
        """Apply the transform."""
        if not self.document.settings.myst_bib_files:
            return
        # populate required references from bibliographies
        citation_keys: Dict[str, List[nodes.citation_reference]] = {}
        for node in self.document.traverse(nodes.citation_reference):
            if "myst-citation-ref" not in node.attributes.get("classes", ()):
                continue
            citation_keys.setdefault(node["refname"], []).append(node)
        if not citation_keys:
            return
        # read bibliographies
        # TODO you would want to cache this in sphinx
        bib_data = {}
        for bibliography in self.document.settings.myst_bib_files:
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
            bib_data.update(parser(bib_bytes))  # TODO check read format, handle clashes
        for idx, citation_key in enumerate(citation_keys, start=1):
            # TODO option to have other labels, e.g. alphabetic or just the refname
            label = str(idx)
            if citation_key not in bib_data:
                # TODO handle warnings and/or remove the reference?
                continue
            for citation_ref in citation_keys[citation_key]:
                if self.sphinx_env:
                    # TODO could not parse the label this way if it is not the key
                    citation_ref["classes"].append(f"myst-cite-label-{label}")
                    citation_ref += nodes.Text(
                        f"myst-{self.sphinx_env.docname}-{citation_key}"
                    )
                else:
                    citation_ref += nodes.Text(label)
            # TODO record which file the citation came from?
            citation = nodes.citation(citation_key, classes=["myst-citation-def"])
            if self.sphinx_env:
                citation["classes"].append(f"myst-cite-label-{label}")
                citation += nodes.label(
                    "", f"myst-{self.sphinx_env.docname}-{citation_key}"
                )
            else:
                citation += nodes.label("", label)
            citation["names"].append(citation_key)
            citation.source = self.document["source"]
            # TODO obviously this would be configurable
            # (also HTML definitions lists get formatted weird if the `dd` is empty)
            text = bib_data[citation_key].get("description", "-")
            citation += nodes.Text(text)
            # TODO citations are currently added to the bottom of the document,
            # but what about ordering of citations vs footnotes
            # also do we want to add a (configured) heading/rubric
            # or let the user decide where they are placed
            self.document += citation
            self.document.note_citation(citation)
            self.document.note_explicit_target(citation, citation)
