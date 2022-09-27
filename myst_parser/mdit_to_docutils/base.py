"""Convert Markdown-it tokens to docutils nodes."""
from __future__ import annotations

import inspect
import json
import os
import re
from collections import OrderedDict
from contextlib import contextmanager
from datetime import date, datetime
from types import ModuleType
from typing import TYPE_CHECKING, Any, Iterator, MutableMapping, Sequence, cast
from urllib.parse import urlparse

import jinja2
import yaml
from docutils import nodes
from docutils.frontend import OptionParser
from docutils.languages import get_language
from docutils.parsers.rst import Directive, DirectiveError
from docutils.parsers.rst import Parser as RSTParser
from docutils.parsers.rst import directives, roles
from docutils.parsers.rst.directives.misc import Include
from docutils.parsers.rst.languages import get_language as get_language_rst
from docutils.statemachine import StringList
from docutils.transforms.components import Filter
from docutils.utils import Reporter, new_document
from docutils.utils.code_analyzer import Lexer, LexerError, NumberLines
from markdown_it import MarkdownIt
from markdown_it.common.utils import escapeHtml
from markdown_it.renderer import RendererProtocol
from markdown_it.token import Token
from markdown_it.tree import SyntaxTreeNode

from myst_parser._compat import findall
from myst_parser.config.main import MdParserConfig
from myst_parser.mocking import (
    MockIncludeDirective,
    MockingError,
    MockInliner,
    MockRSTParser,
    MockState,
    MockStateMachine,
)
from myst_parser.parsers.directives import DirectiveParsingError, parse_directive_text
from .html_to_nodes import html_to_nodes
from .utils import is_external_url

if TYPE_CHECKING:
    from sphinx.environment import BuildEnvironment


def make_document(source_path="notset", parser_cls=RSTParser) -> nodes.document:
    """Create a new docutils document, with the parser classes' default settings."""
    settings = OptionParser(components=(parser_cls,)).get_default_values()
    return new_document(source_path, settings=settings)


REGEX_DIRECTIVE_START = re.compile(r"^[\s]{0,3}([`]{3,10}|[~]{3,10}|[:]{3,10})\{")


def token_line(token: SyntaxTreeNode, default: int | None = None) -> int:
    """Retrieve the initial line of a token."""
    if not getattr(token, "map", None):
        if default is not None:
            return default
        raise ValueError(f"token map not set: {token}")
    return token.map[0]  # type: ignore[index]


def create_warning(
    document: nodes.document,
    message: str,
    *,
    line: int | None = None,
    append_to: nodes.Element | None = None,
    wtype: str = "myst",
    subtype: str = "other",
) -> nodes.system_message | None:
    """Generate a warning, logging if it is necessary.

    Note this is overridden in the ``SphinxRenderer``,
    to handle suppressed warning types.
    """
    kwargs = {"line": line} if line is not None else {}
    msg_node = document.reporter.warning(f"{message} [{wtype}.{subtype}]", **kwargs)
    if append_to is not None:
        append_to.append(msg_node)
    return msg_node


class DocutilsRenderer(RendererProtocol):
    """A markdown-it-py renderer to populate (in-place) a `docutils.document` AST.

    Note, this render is not dependent on Sphinx.
    """

    __output__ = "docutils"

    def __init__(self, parser: MarkdownIt) -> None:
        """Load the renderer (called by ``MarkdownIt``)"""
        self.md = parser
        self.rules = {
            k: v
            for k, v in inspect.getmembers(self, predicate=inspect.ismethod)
            if k.startswith("render_") and k != "render_children"
        }

    def __getattr__(self, name: str):
        """Warn when the renderer has not been setup yet."""
        if name in (
            "md_env",
            "md_config",
            "md_options",
            "document",
            "current_node",
            "reporter",
            "language_module_rst",
            "_level_to_elem",
        ):
            raise AttributeError(
                f"'{name}' attribute is not available until setup_render() is called"
            )
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

    def setup_render(
        self, options: dict[str, Any], env: MutableMapping[str, Any]
    ) -> None:
        """Setup the renderer with per render variables."""
        self.md_env = env
        self.md_options = options
        self.md_config: MdParserConfig = options["myst_config"]
        self.document: nodes.document = options.get("document", make_document())
        self.current_node: nodes.Element = options.get("current_node", self.document)
        self.reporter: Reporter = self.document.reporter
        # note there are actually two possible language modules:
        # one from docutils.languages, and one from docutils.parsers.rst.languages
        self.language_module_rst: ModuleType = get_language_rst(
            self.document.settings.language_code
        )
        # a mapping of heading levels to its currently associated node
        self._level_to_elem: dict[int, nodes.document | nodes.section] = {
            0: self.document
        }

    @property
    def sphinx_env(self) -> BuildEnvironment | None:
        """Return the sphinx env, if using Sphinx."""
        try:
            return self.document.settings.env
        except AttributeError:
            return None

    def create_warning(
        self,
        message: str,
        *,
        line: int | None = None,
        append_to: nodes.Element | None = None,
        wtype: str = "myst",
        subtype: str = "other",
    ) -> nodes.system_message | None:
        """Generate a warning, logging if it is necessary.

        Note this is overridden in the ``SphinxRenderer``,
        to handle suppressed warning types.
        """
        return create_warning(
            self.document,
            message,
            line=line,
            append_to=append_to,
            wtype=wtype,
            subtype=subtype,
        )

    def _render_tokens(self, tokens: list[Token]) -> None:
        """Render the tokens."""
        # propagate line number down to inline elements
        for token in tokens:
            if not token.map:
                continue
            # For docutils we want 1 based line numbers (not 0)
            token.map = [token.map[0] + 1, token.map[1] + 1]
            for token_child in token.children or []:
                token_child.map = token.map

        # nest tokens
        node_tree = SyntaxTreeNode(tokens)

        # move footnote definitions to env
        self.md_env.setdefault("foot_refs", {})
        for node in node_tree.walk(include_self=True):
            new_children = []
            for child in node.children:
                if child.type == "footnote_reference":
                    label = child.meta["label"]
                    self.md_env["foot_refs"].setdefault(label, []).append(child)
                else:
                    new_children.append(child)

            node.children = new_children

        # render
        for child in node_tree.children:
            # skip hidden?
            if f"render_{child.type}" in self.rules:
                self.rules[f"render_{child.type}"](child)
            else:
                self.create_warning(
                    f"No render method for: {child.type}",
                    line=token_line(child, default=0),
                    subtype="render",
                    append_to=self.current_node,
                )

    def render(
        self, tokens: Sequence[Token], options, md_env: MutableMapping[str, Any]
    ) -> nodes.document:
        """Run the render on a token stream.

        :param tokens: list on block tokens to render
        :param options: params of parser instance
        :param md_env: the markdown-it environment sandbox associated with the tokens,
            containing additional metadata like reference info
        """
        self.setup_render(options, md_env)
        self._render_initialise()
        self._render_tokens(list(tokens))
        self._render_finalise()
        return self.document

    def _render_initialise(self) -> None:
        """Initialise the render of the document."""
        self.current_node.extend(
            html_meta_to_nodes(
                self.md_config.html_meta,
                document=self.document,
                line=0,
                reporter=self.reporter,
            )
        )

    def _render_finalise(self) -> None:
        """Finalise the render of the document."""

        # log warnings for duplicate reference definitions
        # "duplicate_refs": [{"href": "ijk", "label": "B", "map": [4, 5], "title": ""}],
        for dup_ref in self.md_env.get("duplicate_refs", []):
            self.create_warning(
                f"Duplicate reference definition: {dup_ref['label']}",
                line=dup_ref["map"][0] + 1,
                subtype="ref",
                append_to=self.document,
            )

        # we don't use the foot_references stored in the env
        # since references within directives/roles will have been added after
        # those from the initial markdown parse
        # instead we gather them from a walk of the created document
        foot_refs = OrderedDict()
        for refnode in findall(self.document)(nodes.footnote_reference):
            if refnode["refname"] not in foot_refs:
                foot_refs[refnode["refname"]] = True

        if foot_refs and self.md_config.footnote_transition:
            self.current_node.append(nodes.transition(classes=["footnotes"]))
        for footref in foot_refs:
            foot_ref_tokens = self.md_env["foot_refs"].get(footref, [])
            if len(foot_ref_tokens) > 1:
                self.create_warning(
                    f"Multiple footnote definitions found for label: '{footref}'",
                    subtype="footnote",
                    append_to=self.current_node,
                )

            if len(foot_ref_tokens) < 1:
                self.create_warning(
                    f"No footnote definitions found for label: '{footref}'",
                    subtype="footnote",
                    append_to=self.current_node,
                )
            else:
                self.render_footnote_reference(foot_ref_tokens[0])

        # Add the wordcount, generated by the ``mdit_py_plugins.wordcount_plugin``.
        wordcount_metadata = self.md_env.get("wordcount", {})
        if wordcount_metadata:

            # save the wordcount to the sphinx BuildEnvironment metadata
            if self.sphinx_env is not None:
                meta = self.sphinx_env.metadata.setdefault(self.sphinx_env.docname, {})
                meta["wordcount"] = wordcount_metadata

            # now add the wordcount as substitution definitions,
            # so we can reference them in the document
            for key in ("words", "minutes"):
                value = wordcount_metadata.get(key, None)
                if value is None:
                    continue
                substitution_node = nodes.substitution_definition(
                    str(value), nodes.Text(str(value))
                )
                substitution_node.source = self.document["source"]
                substitution_node["names"].append(f"wordcount-{key}")
                self.document.note_substitution_def(
                    substitution_node, f"wordcount-{key}"
                )

    def nested_render_text(
        self, text: str, lineno: int, inline: bool = False, allow_headings: bool = True
    ) -> None:
        """Render unparsed text (appending to the current node).

        :param text: the text to render
        :param lineno: the starting line number of the text, within the full source
        :param inline: whether the text is inline or block
        :param allow_headings: whether to allow headings in the text
        """
        if inline:
            tokens = self.md.parseInline(text, self.md_env)
        else:
            tokens = self.md.parse(text + "\n", self.md_env)

        # remove front matter, if present, e.g. from included documents
        if tokens and tokens[0].type == "front_matter":
            tokens.pop(0)

        # update the line numbers
        for token in tokens:
            if token.map:
                token.map = [token.map[0] + lineno, token.map[1] + lineno]

        current_match_titles = self.md_env.get("match_titles", None)
        try:
            self.md_env["match_titles"] = allow_headings
            self._render_tokens(tokens)
        finally:
            self.md_env["match_titles"] = current_match_titles

    @contextmanager
    def current_node_context(
        self, node: nodes.Element, append: bool = False
    ) -> Iterator:
        """Context manager for temporarily setting the current node."""
        if append:
            self.current_node.append(node)
        current_node = self.current_node
        self.current_node = node
        yield
        self.current_node = current_node

    def render_children(self, token: SyntaxTreeNode) -> None:
        """Render the children of a token."""
        for child in token.children or []:
            if f"render_{child.type}" in self.rules:
                self.rules[f"render_{child.type}"](child)
            else:
                self.create_warning(
                    f"No render method for: {child.type}",
                    line=token_line(child, default=0),
                    subtype="render",
                    append_to=self.current_node,
                )

    def add_line_and_source_path(self, node, token: SyntaxTreeNode) -> None:
        """Copy the line number and document source path to the docutils node."""
        try:
            node.line = token_line(token)
        except ValueError:
            pass
        node.source = self.document["source"]

    def add_line_and_source_path_r(
        self, nodes: list[nodes.Element], token: SyntaxTreeNode
    ) -> None:
        """Copy the line number and document source path to the docutils nodes,
        and recursively to all descendants.
        """
        for node in nodes:
            self.add_line_and_source_path(node, token)
            for child in findall(node)():
                self.add_line_and_source_path(child, token)

    def update_section_level_state(self, section: nodes.section, level: int) -> None:
        """Update the section level state, with the new current section and level."""
        # find the closest parent section
        parent_level = max(
            section_level
            for section_level in self._level_to_elem
            if level > section_level
        )
        parent = self._level_to_elem[parent_level]

        # if we are jumping up to a non-consecutive level,
        # then warn about this, since this will not be propagated in the docutils AST
        if (level > parent_level) and (parent_level + 1 != level):
            msg = f"Non-consecutive header level increase; H{parent_level} to H{level}"
            if parent_level == 0:
                msg = f"Document headings start at H{level}, not H1"
            self.create_warning(
                msg,
                line=section.line,
                subtype="header",
                append_to=self.current_node,
            )

        # append the new section to the parent
        parent.append(section)
        # update the state for this section level
        self._level_to_elem[level] = section

        # Remove all descendant sections from the section level state
        self._level_to_elem = {
            section_level: section
            for section_level, section in self._level_to_elem.items()
            if section_level <= level
        }

    def renderInlineAsText(self, tokens: list[SyntaxTreeNode]) -> str:
        """Special kludge for image `alt` attributes to conform CommonMark spec.

        Don't try to use it! Spec requires to show `alt` content with stripped markup,
        instead of simple escaping.
        """
        result = ""

        for token in tokens or []:
            if token.type == "text":
                result += token.content
            # elif token.type == "image":
            #     result += self.renderInlineAsText(token.children)
            else:
                result += self.renderInlineAsText(token.children or [])
        return result

    # ### render methods for commonmark tokens

    def render_paragraph(self, token: SyntaxTreeNode) -> None:
        para = nodes.paragraph(token.children[0].content if token.children else "")
        self.add_line_and_source_path(para, token)
        with self.current_node_context(para, append=True):
            self.render_children(token)

    def render_inline(self, token: SyntaxTreeNode) -> None:
        self.render_children(token)

    def render_text(self, token: SyntaxTreeNode) -> None:
        self.current_node.append(nodes.Text(token.content))

    def render_bullet_list(self, token: SyntaxTreeNode) -> None:
        list_node = nodes.bullet_list()
        if token.markup:
            list_node["bullet"] = token.markup
        if token.attrs.get("class"):
            # this is used e.g. by tasklist
            list_node["classes"] = str(token.attrs["class"]).split()
        self.add_line_and_source_path(list_node, token)
        with self.current_node_context(list_node, append=True):
            self.render_children(token)

    def render_ordered_list(self, token: SyntaxTreeNode) -> None:
        list_node = nodes.enumerated_list(enumtype="arabic", prefix="")
        list_node["suffix"] = token.markup  # for CommonMark, this should be "." or ")"
        if "start" in token.attrs:  # starting number
            list_node["start"] = token.attrs["start"]
        self.add_line_and_source_path(list_node, token)
        with self.current_node_context(list_node, append=True):
            self.render_children(token)

    def render_list_item(self, token: SyntaxTreeNode) -> None:
        item_node = nodes.list_item()
        if token.attrs.get("class"):
            # this is used e.g. by tasklist
            item_node["classes"] = str(token.attrs["class"]).split()
        self.add_line_and_source_path(item_node, token)
        with self.current_node_context(item_node, append=True):
            self.render_children(token)

    def render_em(self, token: SyntaxTreeNode) -> None:
        node = nodes.emphasis()
        self.add_line_and_source_path(node, token)
        with self.current_node_context(node, append=True):
            self.render_children(token)

    def render_softbreak(self, token: SyntaxTreeNode) -> None:
        self.current_node.append(nodes.Text("\n"))

    def render_hardbreak(self, token: SyntaxTreeNode) -> None:
        self.current_node.append(nodes.raw("", "<br />\n", format="html"))
        self.current_node.append(nodes.raw("", "\\\\\n", format="latex"))

    def render_strong(self, token: SyntaxTreeNode) -> None:
        node = nodes.strong()
        self.add_line_and_source_path(node, token)
        with self.current_node_context(node, append=True):
            self.render_children(token)

    def render_blockquote(self, token: SyntaxTreeNode) -> None:
        quote = nodes.block_quote()
        self.add_line_and_source_path(quote, token)
        with self.current_node_context(quote, append=True):
            self.render_children(token)

    def render_hr(self, token: SyntaxTreeNode) -> None:
        node = nodes.transition()
        self.add_line_and_source_path(node, token)
        self.current_node.append(node)

    def render_code_inline(self, token: SyntaxTreeNode) -> None:
        node = nodes.literal(token.content, token.content)
        self.add_line_and_source_path(node, token)
        self.current_node.append(node)

    def create_highlighted_code_block(
        self,
        text: str,
        lexer_name: str | None,
        number_lines: bool = False,
        lineno_start: int = 1,
        source: str | None = None,
        line: int | None = None,
        node_cls: type[nodes.Element] = nodes.literal_block,
    ) -> nodes.Element:
        """Create a literal block with syntax highlighting.

        This mimics the behaviour of the `code-block` directive.

        In docutils, this directive directly parses the text with the pygments lexer,
        whereas in sphinx, the lexer name is only recorded as the `language` attribute,
        and the text is lexed later by pygments within the `visit_literal_block`
        method of the output format ``SphinxTranslator``.

        Note, this function does not add the literal block to the document.
        """
        if self.sphinx_env is not None:
            node = node_cls(text, text, language=lexer_name or "none")
            if number_lines:
                node["linenos"] = True
                if lineno_start != 1:
                    node["highlight_args"] = {"linenostart": lineno_start}
        else:
            node = node_cls(
                text, classes=["code"] + ([lexer_name] if lexer_name else [])
            )
            try:
                lex_tokens = Lexer(
                    text,
                    lexer_name or "",
                    "short" if self.md_config.highlight_code_blocks else "none",
                )
            except LexerError as err:
                self.reporter.warning(
                    str(err),
                    **{
                        name: value
                        for name, value in (("source", source), ("line", line))
                        if value is not None
                    },
                )
                lex_tokens = Lexer(text, lexer_name or "", "none")

            if number_lines:
                lex_tokens = NumberLines(
                    lex_tokens, lineno_start, lineno_start + len(text.splitlines())
                )

            for classes, value in lex_tokens:
                if classes:
                    node += nodes.inline(value, value, classes=classes)
                else:
                    # insert as Text to decrease the verbosity of the output
                    node += nodes.Text(value)

        if source is not None:
            node.source = source
        if line is not None:
            node.line = line
        return node

    def render_code_block(self, token: SyntaxTreeNode) -> None:
        lexer = token.info.split()[0] if token.info else None
        node = self.create_highlighted_code_block(
            token.content,
            lexer,
            source=self.document["source"],
            line=token_line(token, 0) or None,
        )
        self.current_node.append(node)

    def render_fence(self, token: SyntaxTreeNode) -> None:
        text = token.content
        # Ensure that we'll have an empty string if info exists but is only spaces
        info = token.info.strip() if token.info else token.info
        language = info.split()[0] if info else ""

        if (not self.md_config.commonmark_only) and (not self.md_config.gfm_only):
            if language == "{eval-rst}":
                return self.render_restructuredtext(token)
            if language.startswith("{") and language.endswith("}"):
                return self.render_directive(token)

        if not language and self.sphinx_env is not None:
            # use the current highlight setting, via the ``highlight`` directive,
            # or ``highlight_language`` configuration.
            language = self.sphinx_env.temp_data.get(
                "highlight_language", self.sphinx_env.config.highlight_language
            )

        node = self.create_highlighted_code_block(
            text,
            language,
            number_lines=language in self.md_config.number_code_blocks,
            source=self.document["source"],
            line=token_line(token, 0) or None,
        )
        self.current_node.append(node)

    @property
    def blocks_mathjax_processing(self) -> bool:
        """Only add mathjax ignore classes if using sphinx,
        and using the ``dollarmath`` extension, and ``myst_update_mathjax=True``.
        """
        return (
            self.sphinx_env is not None
            and "dollarmath" in self.md_config.enable_extensions
            and self.md_config.update_mathjax
        )

    def render_heading(self, token: SyntaxTreeNode) -> None:
        """Render a heading, e.g. `# Heading`."""

        if self.md_env.get("match_titles", None) is False:
            # this can occur if a nested parse is performed by a directive
            # (such as an admonition) which contains a header.
            # this would break the document structure
            self.create_warning(
                "Disallowed nested header found, converting to rubric",
                line=token_line(token, default=0),
                subtype="nested_header",
                append_to=self.current_node,
            )
            rubric = nodes.rubric(token.content, "")
            self.add_line_and_source_path(rubric, token)
            with self.current_node_context(rubric, append=True):
                self.render_children(token)
            return

        level = int(token.tag[1])

        # create the section node
        new_section = nodes.section()
        self.add_line_and_source_path(new_section, token)
        # if a top level section,
        # then add classes to set default mathjax processing to false
        # we then turn it back on, on a per-node basis
        if level == 1 and self.blocks_mathjax_processing:
            new_section["classes"].extend(["tex2jax_ignore", "mathjax_ignore"])

        # update the state of the section levels
        self.update_section_level_state(new_section, level)

        # create the title for this section
        title_node = nodes.title(token.children[0].content if token.children else "")
        self.add_line_and_source_path(title_node, token)
        new_section.append(title_node)
        # render the heading children into the title
        with self.current_node_context(title_node):
            self.render_children(token)

        # create a target reference for the section, based on the heading text
        name = nodes.fully_normalize_name(title_node.astext())
        new_section["names"].append(name)
        self.document.note_implicit_target(new_section, new_section)

        # set the section as the current node for subsequent rendering
        self.current_node = new_section

    def render_link(self, token: SyntaxTreeNode) -> None:
        """Parse `<http://link.com>` or `[text](link "title")` syntax to docutils AST:

        - If `<>` autolink, forward to `render_autolink`
        - If `myst_all_links_external` is True, forward to `render_external_url`
        - If link is an external URL, forward to `render_external_url`
          - External URLs start with a scheme (e.g. `http:`) in `myst_url_schemes`,
            or any scheme if  `myst_url_schemes` is None.
        - Otherwise, forward to `render_internal_link`
        """
        if token.info == "auto":  # handles both autolink and linkify
            return self.render_autolink(token)

        if (
            self.md_config.commonmark_only
            or self.md_config.gfm_only
            or self.md_config.all_links_external
        ):
            return self.render_external_url(token)

        # Check for external URL
        url_scheme = urlparse(cast(str, token.attrGet("href") or "")).scheme
        allowed_url_schemes = self.md_config.url_schemes
        if (allowed_url_schemes is None and url_scheme) or (
            allowed_url_schemes is not None and url_scheme in allowed_url_schemes
        ):
            return self.render_external_url(token)

        return self.render_internal_link(token)

    def render_external_url(self, token: SyntaxTreeNode) -> None:
        """Render link token `[text](link "title")`,
        where the link has been identified as an external URL::

            <reference refuri="link" title="title">
                text

        `text` can contain nested syntax, e.g. `[**bold**](url "title")`.
        """
        ref_node = nodes.reference()
        self.add_line_and_source_path(ref_node, token)
        ref_node["refuri"] = cast(str, token.attrGet("href") or "")
        title = token.attrGet("title")
        if title:
            ref_node["title"] = title
        with self.current_node_context(ref_node, append=True):
            self.render_children(token)

    def render_internal_link(self, token: SyntaxTreeNode) -> None:
        """Render link token `[text](link "title")`,
        where the link has not been identified as an external URL::

            <reference refname="link" title="title">
                text

        `text` can contain nested syntax, e.g. `[**bold**](link "title")`.

        Note, this is overridden by `SphinxRenderer`, to use `pending_xref` nodes.
        """
        ref_node = nodes.reference()
        self.add_line_and_source_path(ref_node, token)
        ref_node["refname"] = cast(str, token.attrGet("href") or "")
        self.document.note_refname(ref_node)
        title = token.attrGet("title")
        if title:
            ref_node["title"] = title
        with self.current_node_context(ref_node, append=True):
            self.render_children(token)

    def render_autolink(self, token: SyntaxTreeNode) -> None:
        refuri = escapeHtml(token.attrGet("href") or "")  # type: ignore[arg-type]
        ref_node = nodes.reference()
        ref_node["refuri"] = refuri
        self.add_line_and_source_path(ref_node, token)
        with self.current_node_context(ref_node, append=True):
            self.render_children(token)

    def render_html_inline(self, token: SyntaxTreeNode) -> None:
        self.render_html_block(token)

    def render_html_block(self, token: SyntaxTreeNode) -> None:
        node_list = html_to_nodes(token.content, token_line(token), self)
        self.current_node.extend(node_list)

    def render_image(self, token: SyntaxTreeNode) -> None:
        img_node = nodes.image()
        self.add_line_and_source_path(img_node, token)
        destination = cast(str, token.attrGet("src") or "")

        if self.md_env.get("relative-images", None) is not None and not is_external_url(
            destination, None, True
        ):
            # make the path relative to an "including" document
            # this is set when using the `relative-images` option of the MyST `include` directive
            destination = os.path.normpath(
                os.path.join(
                    self.md_env.get("relative-images", ""),
                    os.path.normpath(destination),
                )
            )

        img_node["uri"] = destination

        img_node["alt"] = self.renderInlineAsText(token.children or [])
        title = token.attrGet("title")
        if title:
            img_node["title"] = token.attrGet("title")

        # apply other attributes that can be set on the image
        if "class" in token.attrs:
            img_node["classes"].extend(str(token.attrs["class"]).split())
        if "width" in token.attrs:
            try:
                width = directives.length_or_percentage_or_unitless(
                    str(token.attrs["width"])
                )
            except ValueError:
                self.create_warning(
                    f"Invalid width value for image: {token.attrs['width']!r}",
                    line=token_line(token, default=0),
                    subtype="image",
                    append_to=self.current_node,
                )
            else:
                img_node["width"] = width
        if "height" in token.attrs:
            try:
                height = directives.length_or_unitless(str(token.attrs["height"]))
            except ValueError:
                self.create_warning(
                    f"Invalid height value for image: {token.attrs['height']!r}",
                    line=token_line(token, default=0),
                    subtype="image",
                    append_to=self.current_node,
                )
            else:
                img_node["height"] = height
        if "align" in token.attrs:
            if token.attrs["align"] not in ("left", "center", "right"):
                self.create_warning(
                    f"Invalid align value for image: {token.attrs['align']!r}",
                    line=token_line(token, default=0),
                    subtype="image",
                    append_to=self.current_node,
                )
            else:
                img_node["align"] = token.attrs["align"]
        if "id" in token.attrs:
            name = nodes.fully_normalize_name(str(token.attrs["id"]))
            img_node["names"].append(name)
            self.document.note_explicit_target(img_node, img_node)

        self.current_node.append(img_node)

    # ### render methods for plugin tokens

    def render_front_matter(self, token: SyntaxTreeNode) -> None:
        """Pass document front matter data."""
        position = token_line(token, default=0)

        if isinstance(token.content, str):
            try:
                data = yaml.safe_load(token.content)
            except (yaml.parser.ParserError, yaml.scanner.ScannerError):
                self.create_warning(
                    "Malformed YAML",
                    line=position,
                    append_to=self.current_node,
                    subtype="topmatter",
                )
                return
        else:
            data = token.content

        if not isinstance(data, dict):
            self.create_warning(
                f"YAML is not a dict: {type(data)}",
                line=position,
                append_to=self.current_node,
                subtype="topmatter",
            )
            return

        fields = {
            k: v
            for k, v in data.items()
            if k not in ("myst", "mystnb", "substitutions", "html_meta")
        }
        if fields:
            field_list = self.dict_to_fm_field_list(
                fields, language_code=self.document.settings.language_code
            )
            self.current_node.append(field_list)

        if data.get("title") and self.md_config.title_to_header:
            self.nested_render_text(f"# {data['title']}", 0)

    def dict_to_fm_field_list(
        self, data: dict[str, Any], language_code: str, line: int = 0
    ) -> nodes.field_list:
        """Render each key/val pair as a docutils ``field_node``.

        Bibliographic keys below will be parsed as Markdown,
        all others will be left as literal text.

        The field list should be at the start of the document,
        and will then be converted to a `docinfo` node during the
        `docutils.docutils.transforms.frontmatter.DocInfo` transform (priority 340),
        and bibliographic keys (or their translation) will be converted to nodes::

            {'author': docutils.nodes.author,
            'authors': docutils.nodes.authors,
            'organization': docutils.nodes.organization,
            'address': docutils.nodes.address,
            'contact': docutils.nodes.contact,
            'version': docutils.nodes.version,
            'revision': docutils.nodes.revision,
            'status': docutils.nodes.status,
            'date': docutils.nodes.date,
            'copyright': docutils.nodes.copyright,
            'dedication': docutils.nodes.topic,
            'abstract': docutils.nodes.topic}

        Also, the 'dedication' and 'abstract' will be placed outside the `docinfo`,
        and so will always be shown in the document.

        If using sphinx, this `docinfo` node will later be extracted from the AST,
        by the `DoctreeReadEvent` transform (priority 880),
        calling `MetadataCollector.process_doc`.
        In this case keys and values will be converted to strings and stored in
        `app.env.metadata[app.env.docname]`

        See
        https://www.sphinx-doc.org/en/master/usage/restructuredtext/field-lists.html
        for docinfo fields used by sphinx.

        """
        field_list = nodes.field_list()
        field_list.source, field_list.line = self.document["source"], line

        bibliofields = get_language(language_code).bibliographic_fields

        for key, value in data.items():
            if not isinstance(value, (str, int, float, date, datetime)):
                value = json.dumps(value)
            value = str(value)
            body = nodes.paragraph()
            body.source, body.line = self.document["source"], line
            if key in bibliofields:
                with self.current_node_context(body):
                    self.nested_render_text(value, line, inline=True)
            else:
                body += nodes.literal(value, value)

            field_node = nodes.field()
            field_node.source = value
            field_node += nodes.field_name(key, "", nodes.Text(key))
            field_node += nodes.field_body(value, *[body])
            field_list += field_node

        return field_list

    def render_table(self, token: SyntaxTreeNode) -> None:

        # markdown-it table always contains at least a header:
        assert token.children
        header = token.children[0]
        # with one header row
        assert header.children
        header_row = header.children[0]
        assert header_row.children

        # top-level element
        table = nodes.table()
        table["classes"] += ["colwidths-auto"]
        self.add_line_and_source_path(table, token)
        self.current_node.append(table)

        # column settings element
        maxcols = len(header_row.children)
        colwidths = [100 // maxcols] * maxcols
        tgroup = nodes.tgroup(cols=len(colwidths))
        table += tgroup
        for colwidth in colwidths:
            colspec = nodes.colspec(colwidth=colwidth)
            tgroup += colspec

        # header
        thead = nodes.thead()
        tgroup += thead
        with self.current_node_context(thead):
            self.render_table_row(header_row)

        # body
        if len(token.children) > 1:
            body = token.children[1]
            tbody = nodes.tbody()
            tgroup += tbody
            with self.current_node_context(tbody):
                for body_row in body.children or []:
                    self.render_table_row(body_row)

    def render_table_row(self, token: SyntaxTreeNode) -> None:
        row = nodes.row()
        with self.current_node_context(row, append=True):
            for child in token.children or []:
                entry = nodes.entry()
                para = nodes.paragraph(
                    child.children[0].content if child.children else ""
                )
                style = child.attrGet("style")  # i.e. the alignment when using e.g. :--
                if style and style in (
                    "text-align:left",
                    "text-align:right",
                    "text-align:center",
                ):
                    entry["classes"].append(f"text-{cast(str, style).split(':')[1]}")
                with self.current_node_context(entry, append=True):
                    with self.current_node_context(para, append=True):
                        self.render_children(child)

    def render_s(self, token: SyntaxTreeNode) -> None:
        """Render a strikethrough token."""
        # TODO strikethrough not currently directly supported in docutils
        self.create_warning(
            "Strikethrough is currently only supported in HTML output",
            line=token_line(token, 0),
            subtype="strikethrough",
            append_to=self.current_node,
        )
        self.current_node.append(nodes.raw("", "<s>", format="html"))
        self.render_children(token)
        self.current_node.append(nodes.raw("", "</s>", format="html"))

    def render_math_inline(self, token: SyntaxTreeNode) -> None:
        content = token.content
        node = nodes.math(content, content)
        self.add_line_and_source_path(node, token)
        self.current_node.append(node)

    def render_math_inline_double(self, token: SyntaxTreeNode) -> None:
        content = token.content
        node = nodes.math_block(content, content, nowrap=False, number=None)
        self.add_line_and_source_path(node, token)
        self.current_node.append(node)

    def render_math_single(self, token: SyntaxTreeNode) -> None:
        content = token.content
        node = nodes.math(content, content)
        self.add_line_and_source_path(node, token)
        self.current_node.append(node)

    def render_math_block(self, token: SyntaxTreeNode) -> None:
        content = token.content
        node = nodes.math_block(content, content, nowrap=False, number=None)
        self.add_line_and_source_path(node, token)
        self.current_node.append(node)

    def render_amsmath(self, token: SyntaxTreeNode) -> None:
        # note docutils does not currently support the nowrap attribute
        # or equation numbering, so this is overridden in the sphinx renderer
        node = nodes.math_block(
            token.content, token.content, nowrap=True, classes=["amsmath"]
        )
        if token.meta["numbered"] != "*":
            node["numbered"] = True
        self.add_line_and_source_path(node, token)
        self.current_node.append(node)

    def render_footnote_ref(self, token: SyntaxTreeNode) -> None:
        """Footnote references are added as auto-numbered,
        .i.e. `[^a]` is read as rST `[#a]_`
        """
        target = token.meta["label"]

        refnode = nodes.footnote_reference(f"[^{target}]")
        self.add_line_and_source_path(refnode, token)
        if not target.isdigit():
            refnode["auto"] = 1
            self.document.note_autofootnote_ref(refnode)
        else:
            refnode += nodes.Text(target)

        refnode["refname"] = target
        self.document.note_footnote_ref(refnode)

        self.current_node.append(refnode)

    def render_footnote_reference(self, token: SyntaxTreeNode) -> None:
        target = token.meta["label"]

        footnote = nodes.footnote()
        self.add_line_and_source_path(footnote, token)
        footnote["names"].append(target)
        if not target.isdigit():
            footnote["auto"] = 1
            self.document.note_autofootnote(footnote)
        else:
            footnote += nodes.label("", target)
            self.document.note_footnote(footnote)
        self.document.note_explicit_target(footnote, footnote)
        with self.current_node_context(footnote, append=True):
            self.render_children(token)

    def render_myst_block_break(self, token: SyntaxTreeNode) -> None:
        block_break = nodes.comment(token.content, token.content)
        block_break["classes"] += ["block_break"]
        self.add_line_and_source_path(block_break, token)
        self.current_node.append(block_break)

    def render_myst_target(self, token: SyntaxTreeNode) -> None:
        text = token.content
        name = nodes.fully_normalize_name(text)
        target = nodes.target(text)
        target["names"].append(name)
        self.add_line_and_source_path(target, token)
        self.document.note_explicit_target(target, self.current_node)
        self.current_node.append(target)

    def render_myst_line_comment(self, token: SyntaxTreeNode) -> None:
        self.current_node.append(nodes.comment(token.content, token.content.strip()))

    def render_myst_role(self, token: SyntaxTreeNode) -> None:
        name = token.meta["name"]
        text = token.content
        rawsource = f":{name}:`{token.content}`"
        lineno = token_line(token) if token.map else 0
        role_func, messages = roles.role(
            name, self.language_module_rst, lineno, self.reporter
        )
        inliner = MockInliner(self)
        if role_func:
            nodes, messages2 = role_func(name, rawsource, text, lineno, inliner)
            # return nodes, messages + messages2
            self.current_node += nodes
        else:
            message = self.reporter.error(
                f'Unknown interpreted text role "{name}".', line=lineno
            )
            problematic = inliner.problematic(text, rawsource, message)
            self.current_node += problematic

    def render_colon_fence(self, token: SyntaxTreeNode) -> None:
        """Render a code fence with ``:`` colon delimiters."""

        if token.content.startswith(":::"):
            # the content starts with a nested fence block,
            # but must distinguish between ``:options:``, so we add a new line
            assert token.token is not None, '"colon_fence" must have a `token`'
            linear_token = token.token.copy()
            linear_token.content = "\n" + linear_token.content
            token.token = linear_token

        return self.render_fence(token)

    def render_dl(self, token: SyntaxTreeNode) -> None:
        """Render a definition list."""
        node = nodes.definition_list(classes=["simple", "myst"])
        self.add_line_and_source_path(node, token)
        with self.current_node_context(node, append=True):
            item = None
            for child in token.children or []:
                if child.type == "dt":
                    item = nodes.definition_list_item()
                    self.add_line_and_source_path(item, child)
                    with self.current_node_context(item, append=True):
                        term = nodes.term(
                            child.children[0].content if child.children else ""
                        )
                        self.add_line_and_source_path(term, child)
                        with self.current_node_context(term, append=True):
                            self.render_children(child)
                elif child.type == "dd":
                    if item is None:
                        error = self.reporter.error(
                            (
                                "Found a definition in a definition list, "
                                "with no preceding term"
                            ),
                            # nodes.literal_block(content, content),
                            line=token_line(child),
                        )
                        self.current_node += [error]
                    with self.current_node_context(item):
                        definition = nodes.definition()
                        self.add_line_and_source_path(definition, child)
                        with self.current_node_context(definition, append=True):
                            self.render_children(child)
                else:
                    error_msg = self.reporter.error(
                        (
                            "Expected a term/definition as a child of a definition list"
                            f", but found a: {child.type}"
                        ),
                        # nodes.literal_block(content, content),
                        line=token_line(child),
                    )
                    self.current_node += [error_msg]

    def render_field_list(self, token: SyntaxTreeNode) -> None:
        """Render a field list."""
        field_list = nodes.field_list(classes=["myst"])
        self.add_line_and_source_path(field_list, token)
        with self.current_node_context(field_list, append=True):
            # raise ValueError(token.pretty(show_text=True))
            children = (token.children or [])[:]
            while children:
                child = children.pop(0)
                if not child.type == "fieldlist_name":
                    error_msg = self.reporter.error(
                        (
                            "Expected a fieldlist_name as a child of a field_list"
                            f", but found a: {child.type}"
                        ),
                        # nodes.literal_block(content, content),
                        line=token_line(child),
                    )
                    self.current_node += [error_msg]
                    break
                field = nodes.field()
                self.add_line_and_source_path(field, child)
                field_list += field
                field_name = nodes.field_name()
                self.add_line_and_source_path(field_name, child)
                field += field_name
                with self.current_node_context(field_name):
                    self.render_children(child)
                field_body = nodes.field_body()
                self.add_line_and_source_path(field_name, child)
                field += field_body
                if children and children[0].type == "fieldlist_body":
                    child = children.pop(0)
                    with self.current_node_context(field_body):
                        self.render_children(child)

    def render_restructuredtext(self, token: SyntaxTreeNode) -> None:
        """Render the content of the token as restructuredtext."""
        # copy necessary elements (source, line no, env, reporter)
        newdoc = make_document()
        newdoc["source"] = self.document["source"]
        newdoc.settings = self.document.settings
        newdoc.reporter = self.reporter
        # pad the line numbers artificially so they offset with the fence block
        pseudosource = ("\n" * token_line(token)) + token.content
        # actually parse the rst into our document
        MockRSTParser().parse(pseudosource, newdoc)
        for node in newdoc:
            if node["names"]:
                self.document.note_explicit_target(node, node)
        self.current_node.extend(newdoc.children)

    def render_directive(self, token: SyntaxTreeNode) -> None:
        """Render special fenced code blocks as directives."""
        first_line = token.info.split(maxsplit=1)
        name = first_line[0][1:-1]
        arguments = "" if len(first_line) == 1 else first_line[1]
        content = token.content
        position = token_line(token)
        nodes_list = self.run_directive(name, arguments, content, position)
        self.current_node += nodes_list

    def run_directive(
        self, name: str, first_line: str, content: str, position: int
    ) -> list[nodes.Element]:
        """Run a directive and return the generated nodes.

        :param name: the name of the directive
        :param first_line: The text on the same line as the directive name.
            May be an argument or body text, dependent on the directive
        :param content: All text after the first line. Can include options.
        :param position: The line number of the first line

        """
        # TODO directive name white/black lists

        self.document.current_line = position

        # get directive class
        output: tuple[Directive, list] = directives.directive(
            name, self.language_module_rst, self.document
        )
        directive_class, messages = output
        if not directive_class:
            error = self.reporter.error(
                f'Unknown directive type "{name}".\n',
                # nodes.literal_block(content, content),
                line=position,
            )
            return [error] + messages

        if issubclass(directive_class, Include):
            # this is a Markdown only option,
            # to allow for altering relative image reference links
            directive_class.option_spec["relative-images"] = directives.flag
            directive_class.option_spec["relative-docs"] = directives.path

        try:
            arguments, options, body_lines, content_offset = parse_directive_text(
                directive_class, first_line, content
            )
        except DirectiveParsingError as error:
            error = self.reporter.error(
                f"Directive '{name}': {error}",
                nodes.literal_block(content, content),
                line=position,
            )
            return [error]

        # initialise directive
        if issubclass(directive_class, Include):
            directive_instance = MockIncludeDirective(
                self,
                name=name,
                klass=directive_class,
                arguments=arguments,
                options=options,
                body=body_lines,
                lineno=position,
            )
        else:
            state_machine = MockStateMachine(self, position)
            state = MockState(self, state_machine, position)
            directive_instance = directive_class(
                name=name,
                # the list of positional arguments
                arguments=arguments,
                # a dictionary mapping option names to values
                options=options,
                # the directive content line by line
                content=StringList(body_lines, self.document["source"]),
                # the absolute line number of the first line of the directive
                lineno=position,
                # the line offset of the first line of the content
                content_offset=content_offset,
                # a string containing the entire directive
                block_text="\n".join(body_lines),
                state=state,
                state_machine=state_machine,
            )

        # run directive
        try:
            result = directive_instance.run()
        except DirectiveError as error:
            msg_node = self.reporter.system_message(
                error.level, error.msg, line=position
            )
            msg_node += nodes.literal_block(content, content)
            result = [msg_node]
        except MockingError as exc:
            error_msg = self.reporter.error(
                "Directive '{}' cannot be mocked: {}: {}".format(
                    name, exc.__class__.__name__, exc
                ),
                nodes.literal_block(content, content),
                line=position,
            )
            return [error_msg]

        assert isinstance(
            result, list
        ), f'Directive "{name}" must return a list of nodes.'
        for i in range(len(result)):
            assert isinstance(
                result[i], nodes.Node
            ), 'Directive "{}" returned non-Node object (index {}): {}'.format(
                name, i, result[i]
            )
        return result

    def render_substitution_inline(self, token: SyntaxTreeNode) -> None:
        """Render inline substitution {{key}}."""
        self.render_substitution(token, inline=True)

    def render_substitution_block(self, token: SyntaxTreeNode) -> None:
        """Render block substitution {{key}}."""
        self.render_substitution(token, inline=False)

    def render_substitution(self, token: SyntaxTreeNode, inline: bool) -> None:
        """Substitutions are rendered by:

        1. Combining global substitutions with front-matter substitutions
           to create a variable context (front-matter takes priority)
        2. Add the sphinx `env` to the variable context (if available)
        3. Create the string content with Jinja2 (passing it the variable context)
        4. If the substitution is inline and not a directive,
           parse to nodes ignoring block syntaxes (like lists or block-quotes),
           otherwise parse to nodes with all syntax rules.

        """
        position = token_line(token)

        # front-matter substitutions take priority over config ones
        variable_context: dict[str, Any] = {**self.md_config.substitutions}
        if self.sphinx_env is not None:
            variable_context["env"] = self.sphinx_env

        # fail on undefined variables
        env = jinja2.Environment(undefined=jinja2.StrictUndefined)

        # try rendering
        try:
            rendered = env.from_string(f"{{{{{token.content}}}}}").render(
                variable_context
            )
        except Exception as error:
            error_msg = self.reporter.error(
                f"Substitution error:{error.__class__.__name__}: {error}",
                line=position,
            )
            self.current_node += [error_msg]
            return

        # handle circular references
        ast = env.parse(f"{{{{{token.content}}}}}")
        references = {
            n.name for n in ast.find_all(jinja2.nodes.Name) if n.name != "env"
        }
        self.document.sub_references = getattr(self.document, "sub_references", set())
        cyclic = references.intersection(self.document.sub_references)
        if cyclic:
            error_msg = self.reporter.error(
                f"circular substitution reference: {cyclic}",
                line=position,
            )
            self.current_node += [error_msg]
            return

        # TODO improve error reporting;
        # at present, for a multi-line substitution,
        # an error may point to a line lower than the substitution
        # should it point to the source of the substitution?
        # or the error message should at least indicate that its a substitution

        # we record used references before nested parsing, then remove them after
        self.document.sub_references.update(references)
        try:
            if inline and not REGEX_DIRECTIVE_START.match(rendered):
                self.nested_render_text(rendered, position, inline=True)
            else:
                self.nested_render_text(rendered, position, allow_headings=False)
        finally:
            self.document.sub_references.difference_update(references)


def html_meta_to_nodes(
    data: dict[str, Any], document: nodes.document, line: int, reporter: Reporter
) -> list[nodes.pending | nodes.system_message]:
    """Replicate the `meta` directive,
    by converting a dictionary to a list of pending meta nodes

    See:
    https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#html-metadata
    """
    if not data:
        return []

    try:
        # if sphinx available
        from sphinx.addnodes import meta as meta_cls
    except ImportError:
        try:
            # docutils >= 0.19
            meta_cls = nodes.meta  # type: ignore
        except AttributeError:
            from docutils.parsers.rst.directives.html import MetaBody

            meta_cls = MetaBody.meta  # type: ignore

    output = []

    for key, value in data.items():
        content = str(value or "")
        meta_node = meta_cls(content)
        meta_node.source = document["source"]
        meta_node.line = line
        meta_node["content"] = content
        try:
            if not content:
                raise ValueError("No content")
            for i, key_part in enumerate(key.split()):
                if "=" not in key_part and i == 0:
                    meta_node["name"] = key_part
                    continue
                if "=" not in key_part:
                    raise ValueError(f"no '=' in {key_part}")
                attr_name, attr_val = key_part.split("=", 1)
                if not (attr_name and attr_val):
                    raise ValueError(f"malformed {key_part}")
                meta_node[attr_name.lower()] = attr_val
        except ValueError as error:
            msg = reporter.error(f'Error parsing meta tag attribute "{key}": {error}.')
            output.append(msg)
            continue

        pending = nodes.pending(
            Filter,
            {"component": "writer", "format": "html", "nodes": [meta_node]},
        )
        document.note_pending(pending)
        output.append(pending)

    return output
