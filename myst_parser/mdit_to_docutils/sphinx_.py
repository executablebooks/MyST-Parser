"""Convert Markdown-it tokens to docutils nodes, including sphinx specific elements."""
from __future__ import annotations

from pathlib import Path
from typing import cast
from uuid import uuid4

from docutils import nodes
from markdown_it.tree import SyntaxTreeNode
from sphinx import addnodes
from sphinx.domains.math import MathDomain
from sphinx.environment import BuildEnvironment
from sphinx.util import logging

from myst_parser.mdit_to_docutils.base import DocutilsRenderer, token_line
from myst_parser.warnings import MystWarnings

LOGGER = logging.getLogger(__name__)


def split_myst_uri(uri: str) -> tuple[str, str, dict[str, bool | str]]:
    """Split `type?key1=value&key2=value#target` to type, target, query."""
    front, *_fragment = uri.split("#", 1)
    reftarget = _fragment[0] if _fragment else ""
    reftype, *_query = front.split("?", 1)
    refquery: dict[str, bool | str] = {}
    if _query:
        for comp in _query[0].split("&"):
            if "=" in comp:
                key, val = comp.split("=", 1)
                refquery[key] = val
            else:
                refquery[comp] = True
    return reftype, reftarget, refquery


class SphinxRenderer(DocutilsRenderer):
    """A markdown-it-py renderer to populate (in-place) a `docutils.document` AST.

    This is sub-class of `DocutilsRenderer` that handles sphinx specific aspects,
    such as cross-referencing.
    """

    @property
    def sphinx_env(self) -> BuildEnvironment:
        return self.document.settings.env

    def add_myst_ref(self, token: SyntaxTreeNode, reference: str) -> None:
        """Render link token `[text](myst:any#ref "title")`"""
        reftype, reftarget, refquery = split_myst_uri(reference)

        for value, key in ((reftype, "type"), (reftarget, "target")):
            if not value:
                self.create_warning(
                    f"No myst reference {key} given in 'myst:{reference}'",
                    MystWarnings.MD_INVALID_URI,
                    line=token_line(token, default=0),
                    append_to=self.current_node,
                )
                return self.render_children(token)

        wrap_node = addnodes.pending_xref(
            refdoc=self.sphinx_env.docname,
            refdomain="myst",
            reftype=reftype,
            reftarget=reftarget,
            refexplicit=len(token.children or []) > 0,
            refquery=refquery,
        )
        title = token.attrGet("title")
        if title:
            wrap_node["title"] = title
        self.add_line_and_source_path(wrap_node, token)
        with self.current_node_context(wrap_node, append=True):
            self.render_children(token)

    def add_local_file_ref(
        self, token: SyntaxTreeNode, rel_path: str, abs_path: Path, fragment: None | str
    ) -> None:
        """Render link token `[text](path/to/file.ext#fragment "title")`"""
        docname = self.sphinx_env.path2doc(str(abs_path))

        if not docname:
            return self.add_local_download_ref(token, rel_path, abs_path, fragment)

        wrap_node = addnodes.pending_xref(
            refdoc=self.sphinx_env.docname,
            refdomain="myst",
            reftype="doc",
            reftarget="/" + docname,  # add `/` to denote an absolute name
            refname=fragment,
            refexplicit=len(token.children or []) > 0,
        )
        title = token.attrGet("title")
        if title:
            wrap_node["title"] = title
        self.add_line_and_source_path(wrap_node, token)
        with self.current_node_context(wrap_node, append=True):
            self.render_children(token)

    def add_local_download_ref(
        self, token: SyntaxTreeNode, rel_path: str, abs_path: Path, fragment: None | str
    ) -> None:
        """Render link token `[text](path/to/file.ext#fragment "title")`,
        which is not a project document.
        """
        # TODO what if fragment?
        wrap_node = addnodes.download_reference(
            refdoc=self.sphinx_env.docname,
            reftarget=str(rel_path),
            classes=["myst"],
        )
        title = token.attrGet("title")
        if title:
            wrap_node["title"] = title
        self.add_line_and_source_path(wrap_node, token)
        self.current_node.append(wrap_node)
        if token.children:
            inner_node = nodes.inline("", "", classes=["xref", "download"])
            self.add_line_and_source_path(inner_node, token)
            wrap_node.append(inner_node)
            with self.current_node_context(inner_node):
                self.render_children(token)
        else:
            # using literal mimics the default `download` role behaviour
            inner_node = nodes.literal(
                str(rel_path), str(rel_path), classes=["xref", "download"]
            )
            self.add_line_and_source_path(inner_node, token)
            wrap_node.append(inner_node)

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
