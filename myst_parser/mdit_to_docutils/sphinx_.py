"""Convert Markdown-it tokens to docutils nodes, including sphinx specific elements."""
from __future__ import annotations

import os
from pathlib import Path
from typing import cast
from urllib.parse import unquote
from uuid import uuid4

from docutils import nodes
from markdown_it.tree import SyntaxTreeNode
from sphinx import addnodes
from sphinx.domains.math import MathDomain
from sphinx.domains.std import StandardDomain
from sphinx.environment import BuildEnvironment
from sphinx.ext.intersphinx import InventoryAdapter
from sphinx.util import logging
from sphinx.util.nodes import clean_astext

from myst_parser import inventory
from myst_parser.mdit_to_docutils.base import DocutilsRenderer
from myst_parser.warnings_ import MystWarnings

LOGGER = logging.getLogger(__name__)


class SphinxRenderer(DocutilsRenderer):
    """A markdown-it-py renderer to populate (in-place) a `docutils.document` AST.

    This is sub-class of `DocutilsRenderer` that handles sphinx specific aspects,
    such as cross-referencing.
    """

    @property
    def sphinx_env(self) -> BuildEnvironment:
        return self.document.settings.env

    def render_internal_link(self, token: SyntaxTreeNode) -> None:
        """Render link token `[text](link "title")`,
        where the link has not been identified as an external URL.
        """
        destination = unquote(cast(str, token.attrGet("href") or ""))

        # make the path relative to an "including" document
        # this is set when using the `relative-docs` option of the MyST `include` directive
        relative_include = self.md_env.get("relative-docs", None)
        if relative_include is not None and destination.startswith(relative_include[0]):
            source_dir, include_dir = relative_include[1:]
            destination = os.path.relpath(
                os.path.join(include_dir, os.path.normpath(destination)), source_dir
            )

        potential_path = (
            Path(self.sphinx_env.doc2path(self.sphinx_env.docname)).parent / destination
            if self.sphinx_env.srcdir  # not set in some test situations
            else None
        )
        if (
            potential_path
            and potential_path.is_file()
            and not any(
                destination.endswith(suffix)
                for suffix in self.sphinx_env.config.source_suffix
            )
        ):
            wrap_node = addnodes.download_reference(
                refdoc=self.sphinx_env.docname,
                reftarget=destination,
                reftype="myst",
                refdomain=None,  # Added to enable cross-linking
                refexplicit=len(token.children or []) > 0,
                refwarn=False,
            )
            classes = ["xref", "download", "myst"]
            text = destination if not token.children else ""
        else:
            wrap_node = addnodes.pending_xref(
                refdoc=self.sphinx_env.docname,
                reftarget=destination,
                reftype="myst",
                refdomain=None,  # Added to enable cross-linking
                refexplicit=len(token.children or []) > 0,
                refwarn=True,
            )
            classes = ["xref", "myst"]
            text = ""

        self.add_line_and_source_path(wrap_node, token)
        self.copy_attributes(token, wrap_node, ("class", "id", "title"))
        self.current_node.append(wrap_node)

        inner_node = nodes.inline("", text, classes=classes)
        wrap_node.append(inner_node)
        with self.current_node_context(inner_node):
            self.render_children(token)

    def get_inventory_matches(
        self,
        *,
        invs: str | None,
        domains: str | None,
        otypes: str | None,
        target: str | None,
    ) -> list[inventory.InvMatch]:
        return list(
            inventory.filter_sphinx_inventories(
                InventoryAdapter(self.sphinx_env).named_inventory,
                invs=invs,
                domains=domains,
                otypes=otypes,
                targets=target,
            )
        )

    def render_heading(self, token: SyntaxTreeNode) -> None:
        """This extends the docutils method, to allow for the addition of heading ids.
        These ids are computed by the ``markdown-it-py`` ``anchors_plugin``
        as "slugs" which are unique to a document.

        The approach is similar to ``sphinx.ext.autosectionlabel``
        """
        super().render_heading(token)

        if not isinstance(self.current_node, nodes.section):
            return

        # create the slug string
        slug = cast(str, token.attrGet("id"))
        if slug is None:
            return

        section = self.current_node
        doc_slug = (
            self.sphinx_env.doc2path(self.sphinx_env.docname, base=False) + "#" + slug
        )

        # save the reference in the standard domain, so that it can be handled properly
        domain = cast(StandardDomain, self.sphinx_env.get_domain("std"))
        if doc_slug in domain.labels:
            other_doc = self.sphinx_env.doc2path(domain.labels[doc_slug][0])
            self.create_warning(
                f"duplicate label {doc_slug}, other instance in {other_doc}",
                MystWarnings.ANCHOR_DUPE,
                line=section.line,
            )
        labelid = section["ids"][0]
        domain.anonlabels[doc_slug] = self.sphinx_env.docname, labelid
        domain.labels[doc_slug] = (
            self.sphinx_env.docname,
            labelid,
            clean_astext(section[0]),
        )

        self.sphinx_env.metadata[self.sphinx_env.docname]["myst_anchors"] = True
        section["myst-anchor"] = doc_slug

    def render_math_block_label(self, token: SyntaxTreeNode) -> None:
        """Render math with referencable labels, e.g. ``$a=1$ (label)``."""
        label = token.info
        content = token.content
        node = nodes.math_block(
            content, content, nowrap=False, number=None, label=label
        )
        target = self.add_math_target(node)
        self.add_line_and_source_path(target, token)
        self.current_node.append(target)
        self.add_line_and_source_path(node, token)
        self.current_node.append(node)

    def _random_label(self) -> str:
        return str(uuid4())

    def render_amsmath(self, token: SyntaxTreeNode) -> None:
        """Renderer for the amsmath extension."""
        # environment = token.meta["environment"]
        content = token.content

        if token.meta["numbered"] != "*":
            # TODO how to parse and reference labels within environment?
            # for now we give create a unique hash, so the equation will be numbered
            # but there will be no reference clashes
            label = self._random_label()
            node = nodes.math_block(
                content,
                content,
                nowrap=True,
                number=None,
                classes=["amsmath"],
                label=label,
            )
            target = self.add_math_target(node)
            self.add_line_and_source_path(target, token)
            self.current_node.append(target)
        else:
            node = nodes.math_block(
                content, content, nowrap=True, number=None, classes=["amsmath"]
            )
        self.add_line_and_source_path(node, token)
        self.current_node.append(node)

    def add_math_target(self, node: nodes.math_block) -> nodes.target:
        # Code mainly copied from sphinx.directives.patches.MathDirective

        # register label to domain
        domain = cast(MathDomain, self.sphinx_env.get_domain("math"))
        domain.note_equation(self.sphinx_env.docname, node["label"], location=node)
        node["number"] = domain.get_equation_number_for(node["label"])
        node["docname"] = self.sphinx_env.docname

        # create target node
        node_id = nodes.make_id("equation-%s" % node["label"])
        target = nodes.target("", "", ids=[node_id])
        self.document.note_explicit_target(target)
        return target
