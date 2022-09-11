"""Convert Markdown-it tokens to docutils nodes, including sphinx specific elements."""
from __future__ import annotations

import posixpath
from typing import cast
from uuid import uuid4

from docutils import nodes
from markdown_it.tree import SyntaxTreeNode
from sphinx import addnodes
from sphinx.domains.math import MathDomain
from sphinx.environment import BuildEnvironment
from sphinx.util import docname_join, logging

from myst_parser.mdit_to_docutils.base import DocutilsRenderer, token_line
from myst_parser.warnings import MystWarnings

LOGGER = logging.getLogger(__name__)


class SphinxRenderer(DocutilsRenderer):
    """A markdown-it-py renderer to populate (in-place) a `docutils.document` AST.

    This is sub-class of `DocutilsRenderer` that handles sphinx specific aspects,
    such as cross-referencing.
    """

    @property
    def sphinx_env(self) -> BuildEnvironment:
        return self.document.settings.env

    def add_ref_inventory(
        self, token: SyntaxTreeNode, key: str, target: str, query: dict[str, str]
    ) -> None:
        # otherwise create a pending xref, which will be resolved later
        refexplicit = True if (token.info != "auto" and token.children) else False
        wrap_node = addnodes.pending_xref(
            # standard pending attributes
            refdoc=self.sphinx_env.docname,
            refdomain="myst",
            reftype="inv",
            reftarget=target,
            refexplicit=refexplicit,
            # myst:inv specific attributes
            refkey=key,
            refquery=query,
        )
        self.add_line_and_source_path(wrap_node, token, add_title=True)
        with self.current_node_context(wrap_node, append=True):
            self.render_children(token)

    def add_ref_path(
        self, token: SyntaxTreeNode, path: str, target: str, query: dict[str, str]
    ) -> None:
        wrap_node = addnodes.download_reference(
            refdoc=self.sphinx_env.docname,
            reftarget=str(path),
            classes=["myst-file"],
        )
        self.add_line_and_source_path(wrap_node, token, add_title=True)
        self.current_node.append(wrap_node)
        if token.children:
            with self.current_node_context(wrap_node):
                self.render_children(token)
        else:
            inner_node = nodes.literal(str(path), str(path))
            self.add_line_and_source_path(inner_node, token)
            wrap_node.append(inner_node)

    def add_ref_project(
        self, token: SyntaxTreeNode, path: str, target: str, query: dict[str, str]
    ) -> None:

        if not (path or target):
            self.create_warning(
                "No path or target given for project reference",
                MystWarnings.XREF_ERROR,
                line=token_line(token, default=0),
                append_to=self.current_node,
            )
            warn_node = nodes.inline(classes=["myst-ref-error"])
            with self.current_node_context(warn_node, append=True):
                self.render_children(token)
            return

        # find the target document identifier
        docname: str | None = None
        if path == ".":
            docname = self.sphinx_env.docname
        elif path:
            path = posixpath.normpath(path)
            if path.startswith("/"):
                docname = self.sphinx_env.path2doc(path[1:])
            else:
                rel_docname = self.sphinx_env.path2doc(path)
                docname = (
                    docname_join(self.sphinx_env.docname, rel_docname)
                    if rel_docname
                    else None
                )
            if docname is None:
                self.create_warning(
                    f"Path does not have a known document suffix: {path}",
                    MystWarnings.XREF_ERROR,
                    line=token_line(token, default=0),
                    append_to=self.current_node,
                )
                warn_node = nodes.inline(classes=["myst-ref-error"])
                with self.current_node_context(warn_node, append=True):
                    self.render_children(token)
                return

        refexplicit = True if (token.info != "auto" and token.children) else False
        wrap_node = addnodes.pending_xref(
            # standard pending attributes
            refdoc=self.sphinx_env.docname,
            refdomain="myst",
            reftype="project",
            reftarget=target,
            refexplicit=refexplicit,
            # myst:project specific attributes
            refquery=query,
        )
        if docname is not None:
            wrap_node["reftargetdoc"] = docname
        self.add_line_and_source_path(wrap_node, token, add_title=True)
        with self.current_node_context(wrap_node, append=True):
            self.render_children(token)

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
