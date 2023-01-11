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
from sphinx.environment import BuildEnvironment
from sphinx.ext.intersphinx import InventoryAdapter
from sphinx.util import logging

from myst_parser import inventory
from myst_parser.mdit_to_docutils.base import DocutilsRenderer

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
        kwargs = {
            "refdoc": self.sphinx_env.docname,
            "reftype": "myst",
            "refexplicit": len(token.children or []) > 0,
        }
        path_dest, *_path_ids = destination.split("#", maxsplit=1)
        path_id = _path_ids[0] if _path_ids else None
        potential_path = (
            Path(self.sphinx_env.doc2path(self.sphinx_env.docname)).parent / path_dest
            if self.sphinx_env.srcdir  # not set in some test situations
            else None
        )
        if path_dest == "./":
            # this is a special case, where we want to reference the current document
            potential_path = (
                Path(self.sphinx_env.doc2path(self.sphinx_env.docname))
                if self.sphinx_env.srcdir
                else None
            )
        if potential_path and potential_path.is_file():
            docname = self.sphinx_env.path2doc(str(potential_path))
            if docname:
                wrap_node = addnodes.pending_xref(
                    refdomain="doc", reftarget=docname, reftargetid=path_id, **kwargs
                )
                classes = ["xref", "myst"]
                text = ""
            else:
                wrap_node = addnodes.download_reference(
                    refdomain=None, reftarget=path_dest, refwarn=False, **kwargs
                )
                classes = ["xref", "download", "myst"]
                text = destination if not token.children else ""
        else:
            wrap_node = addnodes.pending_xref(
                refdomain=None, reftarget=destination, refwarn=True, **kwargs
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
