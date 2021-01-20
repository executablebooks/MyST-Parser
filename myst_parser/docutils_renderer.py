import inspect
import json
import os
import re
from collections import OrderedDict
from contextlib import contextmanager
from copy import deepcopy
from datetime import date, datetime
from types import ModuleType
from typing import Any, Dict, List, Optional, Union, cast

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
from markdown_it import MarkdownIt
from markdown_it.common.utils import escapeHtml
from markdown_it.token import NestedTokens, Token, nest_tokens
from markdown_it.utils import AttrDict

from myst_parser.mocking import (
    MockIncludeDirective,
    MockingError,
    MockInliner,
    MockRSTParser,
    MockState,
    MockStateMachine,
)
from .html_to_nodes import html_to_nodes
from .parse_directives import DirectiveParsingError, parse_directive_text
from .utils import is_external_url


def make_document(source_path="notset") -> nodes.document:
    """Create a new docutils document."""
    settings = OptionParser(components=(RSTParser,)).get_default_values()
    return new_document(source_path, settings=settings)


REGEX_DIRECTIVE_START = re.compile(r"^[\s]{0,3}([`]{3,10}|[~]{3,10}|[:]{3,10})\{")

# TODO remove deprecated after v0.13.0
# CSS class regex taken from https://www.w3.org/TR/CSS21/syndata.html#characters
REGEX_ADMONTION = re.compile(
    r"\{(?P<name>[a-zA-Z]+)(?P<classes>(?:\,-?[_a-zA-Z]+[_a-zA-Z0-9-]*)*)\}(?P<title>.*)"  # noqa: E501
)
STD_ADMONITIONS = {
    "admonition": nodes.admonition,
    "attention": nodes.attention,
    "caution": nodes.caution,
    "danger": nodes.danger,
    "error": nodes.error,
    "important": nodes.important,
    "hint": nodes.hint,
    "note": nodes.note,
    "tip": nodes.tip,
    "warning": nodes.warning,
}
try:
    from sphinx import addnodes

    STD_ADMONITIONS["seealso"] = addnodes.seealso
except ImportError:
    pass


def token_line(token: Union[Token, NestedTokens], default: Optional[int] = None) -> int:
    """Retrieve the initial line of a token."""
    if not getattr(token, "map", None):
        if default is not None:
            return default
        raise ValueError(f"token map not set: {token}")
    return token.map[0]  # type: ignore[index]


class DocutilsRenderer:
    """A markdown-it-py renderer to populate (in-place) a `docutils.document` AST.

    Note, this render is not dependent on Sphinx.
    """

    __output__ = "docutils"

    def __init__(self, parser: MarkdownIt):
        """Load the renderer (called by ``MarkdownIt``)"""
        self.md = parser
        self.rules = {
            k: v
            for k, v in inspect.getmembers(self, predicate=inspect.ismethod)
            if k.startswith("render_") and k != "render_children"
        }

    def setup_render(self, options: Dict[str, Any], env: Dict[str, Any]):
        self.env = env
        self.config: Dict[str, Any] = options
        self.document: nodes.document = self.config.get("document", make_document())
        self.current_node: nodes.Element = self.config.get(
            "current_node", self.document
        )
        self.reporter: Reporter = self.document.reporter
        # note there are actually two possible language modules:
        # one from docutils.languages, and one from docutils.parsers.rst.languages
        self.language_module_rst: ModuleType = get_language_rst(
            self.document.settings.language_code
        )
        self._level_to_elem: Dict[int, nodes.Element] = {0: self.document}

    def render(self, tokens: List[Token], options, env: AttrDict):
        """Run the render on a token stream.

        :param tokens: list on block tokens to render
        :param options: params of parser instance
        :param env: the environment sandbox associated with the tokens,
            containing additional metadata like reference info
        """
        self.setup_render(options, env)

        # propagate line number down to inline elements
        for token in tokens:
            if token.map:
                # For docutils we want 1 based line numbers (not 0)
                token.map = [token.map[0] + 1, token.map[1] + 1]
            for child in token.children or []:
                child.map = token.map

        # nest tokens
        nested_tokens = nest_tokens(tokens)

        # move footnote definitions to env
        self.env.setdefault("foot_refs", {})
        new_tokens = []
        for nest_token in nested_tokens:
            if nest_token.type == "footnote_reference_open":
                label = nest_token.meta["label"]
                self.env["foot_refs"].setdefault(label, []).append(nest_token)
            else:
                new_tokens.append(nest_token)

        nested_tokens = new_tokens

        # render
        for i, nest_token in enumerate(nested_tokens):
            # skip hidden?
            if f"render_{nest_token.type}" in self.rules:
                self.rules[f"render_{nest_token.type}"](nest_token)
            else:
                self.current_node.append(
                    self.reporter.warning(
                        f"No render method for: {nest_token.type}",
                        line=token_line(nest_token, default=0),
                    )
                )

        # log warnings for duplicate reference definitions
        # "duplicate_refs": [{"href": "ijk", "label": "B", "map": [4, 5], "title": ""}],
        for dup_ref in self.env.get("duplicate_refs", []):
            self.document.append(
                self.reporter.warning(
                    f"Duplicate reference definition: {dup_ref['label']}",
                    line=dup_ref["map"][0] + 1,
                )
            )

        if not self.config.get("output_footnotes", True):
            return self.document

        # we don't use the foot_references stored in the env
        # since references within directives/roles will have been added after
        # those from the initial markdown parse
        # instead we gather them from a walk of the created document
        foot_refs = OrderedDict()
        for refnode in self.document.traverse(nodes.footnote_reference):
            if refnode["refname"] not in foot_refs:
                foot_refs[refnode["refname"]] = True

        if foot_refs and self.config.get("myst_footnote_transition", False):
            self.current_node.append(nodes.transition(classes=["footnotes"]))
        for footref in foot_refs:
            foot_ref_tokens = self.env["foot_refs"].get(footref, [])
            if len(foot_ref_tokens) > 1:
                self.current_node.append(
                    self.reporter.warning(
                        f"Multiple footnote definitions found for label: '{footref}'",
                    )
                )
            if len(foot_ref_tokens) < 1:
                self.current_node.append(
                    self.reporter.warning(
                        f"No footnote definitions found for label: '{footref}'",
                    )
                )
            else:
                self.render_footnote_reference_open(foot_ref_tokens[0])

        return self.document

    def nested_render_text(self, text: str, lineno: int):
        """Render unparsed text."""
        tokens = self.md.parse(text + "\n", self.env)
        if tokens and tokens[0].type == "front_matter":
            tokens.pop(0)

        # set correct line numbers
        for token in tokens:
            if token.map:
                token.map = [token.map[0] + lineno, token.map[1] + lineno]
                for child in token.children or []:
                    child.map = token.map

        # nest tokens
        nested_tokens = nest_tokens(tokens)

        # move footnote definitions to env
        self.env.setdefault("foot_refs", {})
        new_tokens = []
        for nest_token in nested_tokens:
            if nest_token.type == "footnote_reference_open":
                label = nest_token.meta["label"]
                self.env["foot_refs"].setdefault(label, []).append(nest_token)
            else:
                new_tokens.append(nest_token)

        nested_tokens = new_tokens

        # render
        for i, nest_token in enumerate(nested_tokens):
            # skip hidden?
            if f"render_{nest_token.type}" in self.rules:
                self.rules[f"render_{nest_token.type}"](nest_token)
            else:
                self.current_node.append(
                    self.reporter.warning(
                        f"No render method for: {nest_token.type}",
                        line=token_line(nest_token, default=0),
                    )
                )

    @contextmanager
    def current_node_context(self, node: nodes.Element, append: bool = False):
        """Context manager for temporarily setting the current node."""
        if append:
            self.current_node.append(node)
        current_node = self.current_node
        self.current_node = node
        yield
        self.current_node = current_node

    def render_children(self, token: Union[Token, NestedTokens]):
        for i, child in enumerate(token.children or []):
            if f"render_{child.type}" in self.rules:
                self.rules[f"render_{child.type}"](child)
            else:
                self.current_node.append(
                    self.reporter.warning(
                        f"No render method for: {child.type}",
                        line=token_line(child, default=0),
                    )
                )

    def add_line_and_source_path(self, node, token: Union[Token, NestedTokens]):
        """Copy the line number and document source path to the docutils node."""
        try:
            node.line = token_line(token)
        except ValueError:
            pass
        node.source = self.document["source"]

    def is_section_level(self, level, section):
        return self._level_to_elem.get(level, None) == section

    def add_section(self, section, level):
        parent_level = max(
            section_level
            for section_level in self._level_to_elem
            if level > section_level
        )

        if (level > parent_level) and (parent_level + 1 != level):
            self.current_node.append(
                self.reporter.warning(
                    "Non-consecutive header level increase; {} to {}".format(
                        parent_level, level
                    ),
                    line=section.line,
                )
            )

        parent = self._level_to_elem[parent_level]
        parent.append(section)
        self._level_to_elem[level] = section

        # Prune level to limit
        self._level_to_elem = dict(
            (section_level, section)
            for section_level, section in self._level_to_elem.items()
            if section_level <= level
        )

    def renderInlineAsText(self, tokens: List[Token]) -> str:
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

    def render_paragraph_open(self, token: NestedTokens):
        para = nodes.paragraph("")
        self.add_line_and_source_path(para, token)
        with self.current_node_context(para, append=True):
            self.render_children(token)

    def render_inline(self, token: Token):
        self.render_children(token)

    def render_text(self, token: Token):
        self.current_node.append(nodes.Text(token.content, token.content))

    def render_bullet_list_open(self, token: NestedTokens):
        list_node = nodes.bullet_list()
        self.add_line_and_source_path(list_node, token)
        with self.current_node_context(list_node, append=True):
            self.render_children(token)

    def render_ordered_list_open(self, token: Token):
        list_node = nodes.enumerated_list()
        self.add_line_and_source_path(list_node, token)
        with self.current_node_context(list_node, append=True):
            self.render_children(token)

    def render_list_item_open(self, token: NestedTokens):
        item_node = nodes.list_item()
        self.add_line_and_source_path(item_node, token)
        with self.current_node_context(item_node, append=True):
            self.render_children(token)

    def render_em_open(self, token: NestedTokens):
        node = nodes.emphasis()
        self.add_line_and_source_path(node, token)
        with self.current_node_context(node, append=True):
            self.render_children(token)

    def render_softbreak(self, token: Token):
        self.current_node.append(nodes.Text("\n"))

    def render_hardbreak(self, token: Token):
        self.current_node.append(nodes.raw("", "<br />\n", format="html"))

    def render_strong_open(self, token: NestedTokens):
        node = nodes.strong()
        self.add_line_and_source_path(node, token)
        with self.current_node_context(node, append=True):
            self.render_children(token)

    def render_blockquote_open(self, token: NestedTokens):
        quote = nodes.block_quote()
        self.add_line_and_source_path(quote, token)
        with self.current_node_context(quote, append=True):
            self.render_children(token)

    def render_hr(self, token: Token):
        node = nodes.transition()
        self.add_line_and_source_path(node, token)
        self.current_node.append(node)

    def render_code_inline(self, token: Token):
        node = nodes.literal(token.content, token.content)
        self.add_line_and_source_path(node, token)
        self.current_node.append(node)

    def render_code_block(self, token: Token):
        # this should never have a language, since it is just indented text, however,
        # creating a literal_block with no language will raise a warning in sphinx
        text = token.content
        language = token.info.split()[0] if token.info else "none"
        language = language or "none"
        node = nodes.literal_block(text, text, language=language)
        self.add_line_and_source_path(node, token)
        self.current_node.append(node)

    def render_fence(self, token: Token):
        text = token.content
        if token.info:
            # Ensure that we'll have an empty string if info exists but is only spaces
            token.info = token.info.strip()
        language = token.info.split()[0] if token.info else ""

        if not self.config.get("commonmark_only", False) and language == "{eval-rst}":
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
            self.current_node.extend(newdoc[:])
            return
        elif (
            not self.config.get("commonmark_only", False)
            and language.startswith("{")
            and language.endswith("}")
        ):
            return self.render_directive(token)

        if not language:
            try:
                sphinx_env = self.document.settings.env
                language = sphinx_env.temp_data.get(
                    "highlight_language", sphinx_env.config.highlight_language
                )
            except AttributeError:
                pass
        if not language:
            language = self.config.get("highlight_language", "")
        node = nodes.literal_block(text, text, language=language)
        self.add_line_and_source_path(node, token)
        self.current_node.append(node)

    def render_heading_open(self, token: NestedTokens):
        # Test if we're replacing a section level first

        level = int(token.tag[1])
        if isinstance(self.current_node, nodes.section):
            if self.is_section_level(level, self.current_node):
                self.current_node = cast(nodes.Element, self.current_node.parent)

        title_node = nodes.title()
        self.add_line_and_source_path(title_node, token)

        new_section = nodes.section()
        self.add_line_and_source_path(new_section, token)
        new_section.append(title_node)

        self.add_section(new_section, level)

        self.current_node = title_node
        self.render_children(token)

        assert isinstance(self.current_node, nodes.title)
        text = self.current_node.astext()
        # if self.translate_section_name:
        #     text = self.translate_section_name(text)
        name = nodes.fully_normalize_name(text)
        section = cast(nodes.section, self.current_node.parent)
        section["names"].append(name)
        self.document.note_implicit_target(section, section)
        self.current_node = section

    def render_link_open(self, token: NestedTokens):
        if token.markup == "autolink":
            return self.render_autolink(token)

        ref_node = nodes.reference()
        self.add_line_and_source_path(ref_node, token)
        destination = token.attrGet("href") or ""

        if self.config.get(
            "relative-docs", None
        ) is not None and destination.startswith(self.config["relative-docs"][0]):
            # make the path relative to an "including" document
            source_dir, include_dir = self.config["relative-docs"][1:]
            destination = os.path.relpath(
                os.path.join(include_dir, os.path.normpath(destination)), source_dir
            )

        ref_node["refuri"] = destination  # type: ignore[index]

        title = token.attrGet("title")
        if title:
            ref_node["title"] = title  # type: ignore[index]
        next_node = ref_node

        # TODO currently any reference with a fragment # is deemed external
        # (if anchors are not enabled)
        # This comes from recommonmark, but I am not sure of the rationale for it
        if is_external_url(
            destination,
            self.config.get("myst_url_schemes", None),
            "heading_anchors" not in self.config.get("myst_extensions", []),
        ):
            self.current_node.append(next_node)
            with self.current_node_context(ref_node):
                self.render_children(token)
        else:
            self.handle_cross_reference(token, destination)

    def handle_cross_reference(self, token, destination):
        if not self.config.get("ignore_missing_refs", False):
            self.current_node.append(
                self.reporter.warning(
                    f"Reference not found: {destination}", line=token_line(token)
                )
            )

    def render_autolink(self, token: NestedTokens):
        refuri = target = escapeHtml(token.attrGet("href") or "")
        ref_node = nodes.reference(target, target, refuri=refuri)
        self.add_line_and_source_path(ref_node, token)
        self.current_node.append(ref_node)

    def render_html_inline(self, token: Token):
        self.render_html_block(token)

    def render_html_block(self, token: Token):
        node_list = html_to_nodes(token.content, token_line(token), self)
        self.current_node.extend(node_list)

    def render_image(self, token: Token):
        img_node = nodes.image()
        self.add_line_and_source_path(img_node, token)
        destination = token.attrGet("src") or ""

        if self.config.get("relative-images", None) is not None and not is_external_url(
            destination, None, True
        ):
            # make the path relative to an "including" document
            destination = os.path.normpath(
                os.path.join(
                    self.config.get("relative-images", ""),
                    os.path.normpath(destination),
                )
            )

        img_node["uri"] = destination

        img_node["alt"] = self.renderInlineAsText(token.children or [])
        title = token.attrGet("title")
        if title:
            img_node["title"] = token.attrGet("title")
        self.current_node.append(img_node)

    # ### render methods for plugin tokens

    def render_front_matter(self, token: Token):
        """Pass document front matter data."""
        position = token_line(token, default=0)

        if not isinstance(token.content, dict):
            try:
                data = yaml.safe_load(token.content)
            except (yaml.parser.ParserError, yaml.scanner.ScannerError) as error:
                msg_node = self.reporter.error(
                    "Front matter block:\n" + str(error), line=position
                )
                msg_node += nodes.literal_block(token.content, token.content)
                self.current_node.append(msg_node)
                return
        else:
            data = deepcopy(token.content)

        substitutions = data.pop("substitutions", {})
        html_meta = data.pop("html_meta", {})

        if data:
            field_list = self.dict_to_fm_field_list(
                data, language_code=self.document.settings.language_code
            )
            self.current_node.append(field_list)

        if isinstance(substitutions, dict):
            self.document.fm_substitutions = substitutions
        else:
            msg_node = self.reporter.error(
                "Front-matter 'substitutions' is not a dict", line=position
            )
            msg_node += nodes.literal_block(token.content, token.content)
            self.current_node.append(msg_node)

        if not isinstance(html_meta, dict):
            msg_node = self.reporter.error(
                "Front-matter 'html_meta' is not a dict", line=position
            )
            msg_node += nodes.literal_block(token.content, token.content)
            self.current_node.append(msg_node)

        self.current_node.extend(
            html_meta_to_nodes(
                {
                    **self.config.get("myst_html_meta", {}),
                    **html_meta,
                },
                document=self.document,
                line=position,
                reporter=self.reporter,
            )
        )

    def dict_to_fm_field_list(
        self, data: Dict[str, Any], language_code: str, line: int = 0
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

        bibliofields = get_language(language_code).bibliographic_fields
        state_machine = MockStateMachine(self, line)
        state = MockState(self, state_machine, line)

        for key, value in data.items():
            if not isinstance(value, (str, int, float, date, datetime)):
                value = json.dumps(value)
            value = str(value)
            if key in bibliofields:
                para_nodes, _ = state.inline_text(value, line)
                body_children = [nodes.paragraph("", "", *para_nodes)]
            else:
                body_children = [nodes.Text(value, value)]

            field_node = nodes.field()
            field_node.source = value
            field_node += nodes.field_name(key, "", nodes.Text(key, key))
            field_node += nodes.field_body(value, *body_children)
            field_list += field_node

        return field_list

    def render_table_open(self, token: NestedTokens):

        assert token.children and len(token.children) > 1

        # markdown-it table always contains two elements:
        header = token.children[0]
        body = token.children[1]
        # with one header row
        assert header.children
        header_row = cast(Token, header.children[0])
        assert header_row.children

        # top-level element
        table = nodes.table()
        table["classes"] += ["colwidths-auto"]
        self.add_line_and_source_path(table, token)
        self.current_node.append(table)

        # column settings element
        maxcols = len(header_row.children)
        colwidths = [round(100 / maxcols, 2)] * maxcols
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
        tbody = nodes.tbody()
        tgroup += tbody
        with self.current_node_context(tbody):
            for body_row in body.children or []:
                self.render_table_row(cast(Token, body_row))

    def render_table_row(self, token: Token):
        row = nodes.row()
        with self.current_node_context(row, append=True):
            for child in token.children or []:
                entry = nodes.entry()
                para = nodes.paragraph("")
                style = child.attrGet("style")  # i.e. the alignment when using e.g. :--
                if style:
                    entry["classes"].append(style)
                with self.current_node_context(entry, append=True):
                    with self.current_node_context(para, append=True):
                        self.render_children(child)

    def render_math_inline(self, token: Token):
        content = token.content
        node = nodes.math(content, content)
        self.add_line_and_source_path(node, token)
        self.current_node.append(node)

    def render_math_single(self, token: Token):
        content = token.content
        node = nodes.math(content, content)
        self.add_line_and_source_path(node, token)
        self.current_node.append(node)

    def render_math_block(self, token: Token):
        content = token.content
        node = nodes.math_block(content, content, nowrap=False, number=None)
        self.add_line_and_source_path(node, token)
        self.current_node.append(node)

    def render_footnote_ref(self, token: Token):
        """Footnote references are added as auto-numbered,
        .i.e. `[^a]` is read as rST `[#a]_`
        """
        target = token.meta["label"]

        refnode = nodes.footnote_reference("[^{}]".format(target))
        self.add_line_and_source_path(refnode, token)
        if not target.isdigit():
            refnode["auto"] = 1
            self.document.note_autofootnote_ref(refnode)
        else:
            refnode += nodes.Text(target)

        refnode["refname"] = target
        self.document.note_footnote_ref(refnode)

        self.current_node.append(refnode)

    def render_footnote_reference_open(self, token: NestedTokens):
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

    def render_myst_block_break(self, token: Token):
        block_break = nodes.comment(token.content, token.content)
        block_break["classes"] += ["block_break"]
        self.add_line_and_source_path(block_break, token)
        self.current_node.append(block_break)

    def render_myst_target(self, token: Token):
        text = token.content
        name = nodes.fully_normalize_name(text)
        target = nodes.target(text)
        target["names"].append(name)
        self.add_line_and_source_path(target, token)
        self.document.note_explicit_target(target, self.current_node)
        self.current_node.append(target)

    def render_myst_line_comment(self, token: Token):
        self.current_node.append(nodes.comment(token.content, token.content))

    def render_myst_role(self, token: Token):
        name = token.meta["name"]
        text = token.content
        rawsource = f":{name}:`{token.content}`"
        lineno = token_line(token) if token.map else 0
        role_func, messages = roles.role(
            name, self.language_module_rst, lineno, self.reporter
        )
        inliner = MockInliner(self, lineno)
        if role_func:
            nodes, messages2 = role_func(name, rawsource, text, lineno, inliner)
            # return nodes, messages + messages2
            self.current_node += nodes
        else:
            message = self.reporter.error(
                'Unknown interpreted text role "{}".'.format(name), line=lineno
            )
            problematic = inliner.problematic(text, rawsource, message)
            self.current_node += problematic

    def render_colon_fence(self, token: Token):
        """Render a code fence with ``:`` colon delimiters."""

        # TODO remove deprecation after v0.13.0
        match = REGEX_ADMONTION.match(token.info.strip())
        if match and match.groupdict()["name"] in list(STD_ADMONITIONS) + ["figure"]:
            classes = match.groupdict()["classes"][1:].split(",")
            name = match.groupdict()["name"]
            if classes and classes[0]:
                self.current_node.append(
                    self.reporter.warning(
                        "comma-separated classes are deprecated, "
                        "use `:class:` option instead",
                        line=token_line(token),
                    )
                )
                # we assume that no other options have been used
                token.content = f":class: {' '.join(classes)}\n\n" + token.content
            if name == "figure":
                self.current_node.append(
                    self.reporter.warning(
                        ":::{figure} is deprecated, " "use :::{figure-md} instead",
                        line=token_line(token),
                    )
                )
                name = "figure-md"

            token.info = f"{{{name}}} {match.groupdict()['title']}"

        if token.content.startswith(":::"):
            # the content starts with a nested fence block,
            # but must distinguish between ``:options:``, so we add a new line
            token.content = "\n" + token.content

        return self.render_fence(token)

    def render_dl_open(self, token: NestedTokens):
        """Render a definition list."""
        node = nodes.definition_list(classes=["simple", "myst"])
        self.add_line_and_source_path(node, token)
        with self.current_node_context(node, append=True):
            item = None
            for child in token.children or []:
                if isinstance(child, NestedTokens) and child.opening.type == "dt_open":
                    item = nodes.definition_list_item()
                    self.add_line_and_source_path(item, child)
                    with self.current_node_context(item, append=True):
                        term = nodes.term()
                        self.add_line_and_source_path(term, child)
                        with self.current_node_context(term, append=True):
                            self.render_children(child)
                elif (
                    isinstance(child, NestedTokens) and child.opening.type == "dd_open"
                ):
                    if item is None:
                        error = self.reporter.error(
                            (
                                "Found a definition in a definition list, "
                                "with no preceding term"
                            ),
                            # nodes.literal_block(content, content),
                            line=child.map[0],
                        )
                        self.current_node += [error]
                    with self.current_node_context(item):
                        definition = nodes.definition()
                        self.add_line_and_source_path(definition, child)
                        with self.current_node_context(definition, append=True):
                            self.render_children(child)
                else:
                    ctype = (
                        child.opening.type
                        if isinstance(child, NestedTokens)
                        else child.type
                    )
                    error_msg = self.reporter.error(
                        (
                            "Expected a term/definition as a child of a definition list"
                            f", but found a: {ctype}"
                        ),
                        # nodes.literal_block(content, content),
                        line=token_line(child),
                    )
                    self.current_node += [error_msg]

    def render_directive(self, token: Token):
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
    ) -> List[nodes.Element]:
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
        directive_class, messages = directives.directive(
            name, self.language_module_rst, self.document
        )  # type: (Directive, list)
        if not directive_class:
            error = self.reporter.error(
                'Unknown directive type "{}".\n'.format(name),
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
            arguments, options, body_lines = parse_directive_text(
                directive_class, first_line, content
            )
        except DirectiveParsingError as error:
            error = self.reporter.error(
                "Directive '{}': {}".format(name, error),
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
                content_offset=0,  # TODO get content offset from `parse_directive_text`
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
        ), 'Directive "{}" must return a list of nodes.'.format(name)
        for i in range(len(result)):
            assert isinstance(
                result[i], nodes.Node
            ), 'Directive "{}" returned non-Node object (index {}): {}'.format(
                name, i, result[i]
            )
        return result

    def render_substitution_inline(self, token: Token):
        """Render inline substitution {{key}}."""
        self.render_substitution(token, inline=True)

    def render_substitution_block(self, token: Token):
        """Render block substitution {{key}}."""
        self.render_substitution(token, inline=False)

    def render_substitution(self, token, inline: bool):
        """Substitutions are rendered by:

        1. Combining global substitutions with front-matter substitutions
           to create a variable context (front-matter takes priority)
        2. Add the sphinx `env` to the variable context (if available)
        3. Create the string content with Jinja2 (passing it the variable context)
        4. If the substitution is inline and not a directive,
           parse to nodes ignoring block syntaxes (like lists or block-quotes),
           otherwise parse to nodes with all syntax rules.

        """

        # TODO token.map was None when substituting an image in a table
        # (should be fixed: https://github.com/executablebooks/markdown-it-py/pull/109)
        position = token.map[0] if token.map else 9999

        # front-matter substitutions take priority over config ones
        variable_context = {
            **self.config.get("myst_substitutions", {}),
            **getattr(self.document, "fm_substitutions", {}),
        }
        try:
            variable_context["env"] = self.document.settings.env
        except AttributeError:
            pass  # if not sphinx renderer

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

        # parse rendered text
        state_machine = MockStateMachine(self, position)
        state = MockState(self, state_machine, position)

        # TODO improve error reporting;
        # at present, for a multi-line substitution,
        # an error may point to a line lower than the substitution
        # should it point to the source of the substitution?
        # or the error message should at least indicate that its a substitution

        # we record used references before nested parsing, then remove them after
        self.document.sub_references.update(references)

        try:
            if inline and not REGEX_DIRECTIVE_START.match(rendered):
                sub_nodes, _ = state.inline_text(rendered, position)
            else:
                base_node = nodes.Element()
                state.nested_parse(
                    StringList(rendered.splitlines(), self.document["source"]),
                    0,
                    base_node,
                )
                sub_nodes = base_node.children
        finally:
            self.document.sub_references.difference_update(references)

        self.current_node.extend(sub_nodes)


def html_meta_to_nodes(
    data: Dict[str, Any], document: nodes.document, line: int, reporter: Reporter
) -> List[Union[nodes.pending, nodes.system_message]]:
    """Replicate the `meta` directive,
    by converting a dictionary to a list of pending meta nodes

    See:
    https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#html-metadata
    """
    if not data:
        return []

    try:
        from sphinx.addnodes import meta as meta_cls
    except ImportError:
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
