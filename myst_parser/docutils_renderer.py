from contextlib import contextmanager
from itertools import chain
from os.path import splitext
import re
import sys
from typing import List, Optional
from unittest import mock
from urllib.parse import urlparse, unquote
from textwrap import dedent

from docutils import nodes
from docutils.frontend import OptionParser
from docutils.languages import get_language
from docutils.parsers.rst import directives, DirectiveError, roles
from docutils.parsers.rst import Parser as RSTParser
from docutils.parsers.rst.states import RSTStateMachine, Body, Inliner
from docutils.utils import new_document
import yaml

from mistletoe import Document, block_token, span_token
from mistletoe.base_renderer import BaseRenderer

from myst_parser import span_tokens as myst_span_tokens
from myst_parser import block_tokens as myst_block_tokens
from myst_parser.utils import escape_url


class DocutilsRenderer(BaseRenderer):
    """A mistletoe renderer to populate (in-place) a `docutils.document` AST.

    Note this renderer has no dependencies in sphinx.
    """

    def __init__(
        self,
        document: Optional[nodes.document] = None,
        current_node: Optional[nodes.Element] = None,
        config: Optional[dict] = None,
    ):
        """Initialise the renderer.

        Parameters
        ----------
        document : docutils.nodes.document
            The document to populate (or create a new one if None)
        current_node : docutils.nodes.Element
            The root node from which to begin populating (default is document)
            (should be an ancestor of document)
        config : dict
            contains configuration specific to the rendering process

        """
        self.config = config or {}
        self.document = document or self.new_document()  # type: nodes.document
        self.current_node = current_node or self.document  # type: nodes.Element
        self.language_module = self.document.settings.language_code  # type: str
        get_language(self.language_module)
        self._level_to_elem = {0: self.document}

        _span_tokens = self._tokens_from_module(myst_span_tokens)
        _block_tokens = self._tokens_from_module(myst_block_tokens)

        super().__init__(*chain(_block_tokens, _span_tokens))

        span_token._token_types.value = _span_tokens
        block_token._token_types.value = _block_tokens

    def new_document(self, source_name="") -> nodes.document:
        settings = OptionParser(components=(RSTParser,)).get_default_values()
        return new_document(source_name, settings=settings)

    def render_children(self, token):
        for child in token.children:
            self.render(child)

    @contextmanager
    def set_current_node(self, node, append=False):
        if append:
            self.current_node.append(node)
        current_node = self.current_node
        self.current_node = node
        yield
        self.current_node = current_node

    def render_document(self, token):
        # TODO deal with footnotes
        self.footnotes.update(token.footnotes)
        self.render_children(token)
        return self.document

    def render_front_matter(self, token):
        """Pass document front matter data

        For RST, all field lists are captured by
        ``docutils.docutils.parsers.rst.states.Body.field_marker``,
        then, if one occurs at the document, it is transformed by
        `docutils.docutils.transforms.frontmatter.DocInfo`, and finally
        this is intercepted by sphinx and added to the env in
        `sphinx.environment.collectors.metadata.MetadataCollector.process_doc`

        So technically the values should be parsed to AST, but this is redundant,
        since `process_doc` just converts them back to text.

        """
        # TODO this data could be used to support default option values for directives
        docinfo = nodes.docinfo()
        for key, value in token.data.items():
            if not isinstance(value, (str, int, float)):
                continue
            value = str(value)
            field_node = nodes.field()
            field_node.source = value
            field_node += nodes.field_name(key, "", nodes.Text(key, key))
            field_node += nodes.field_body(value, nodes.Text(value, value))
            docinfo += field_node
        self.current_node.append(docinfo)

    def render_paragraph(self, token):
        if len(token.children) == 1 and isinstance(
            token.children[0], myst_span_tokens.Target
        ):
            # promote the target to block level
            return self.render_target(token.children[0])
        para = nodes.paragraph("")
        para.line = token.range[0]
        with self.set_current_node(para, append=True):
            self.render_children(token)

    def render_line_comment(self, token):
        self.current_node.append(nodes.comment(token.content, token.content))

    def render_target(self, token):
        text = token.children[0].content
        name = nodes.fully_normalize_name(text)
        target = nodes.target(text)
        target["names"].append(name)
        self.document.note_explicit_target(target, self.current_node)
        self.current_node.append(target)

    def render_raw_text(self, token):
        text = token.content
        self.current_node.append(nodes.Text(text, text))

    def render_escape_sequence(self, token):
        text = token.children[0].content
        self.current_node.append(nodes.Text(text, text))

    def render_line_break(self, token):
        if token.soft:
            self.current_node.append(nodes.Text("\n"))
        else:
            self.current_node.append(nodes.raw("", "<br />\n", format="html"))

    def render_strong(self, token):
        node = nodes.strong()
        with self.set_current_node(node, append=True):
            self.render_children(token)

    def render_emphasis(self, token):
        node = nodes.emphasis()
        with self.set_current_node(node, append=True):
            self.render_children(token)

    def render_quote(self, token):
        quote = nodes.block_quote()
        quote.line = token.range[0]
        with self.set_current_node(quote, append=True):
            self.render_children(token)

    def render_strikethrough(self, token):
        # TODO there is no existing node/role for this
        raise NotImplementedError

    def render_thematic_break(self, token):
        self.current_node.append(nodes.transition())

    def render_math(self, token):
        if token.content.startswith("$$"):
            content = token.content[2:-2]
            node = nodes.math_block(content, content, nowrap=False, number=None)
        else:
            content = token.content[1:-1]
            node = nodes.math(content, content)
        self.current_node.append(node)

    def render_code_fence(self, token):
        if token.language.startswith("{") and token.language.endswith("}"):
            return self.render_directive(token)
        self.render_block_code(token, default_language=True)

    def render_block_code(self, token, default_language=False):
        # indented code blocks will always have no language,
        # but for code fences, if not set, a default_language will be retrieved
        text = token.children[0].content
        language = token.language
        if not language and default_language:
            try:
                sphinx_env = self.document.settings.env
                language = sphinx_env.temp_data.get(
                    "highlight_language", sphinx_env.config.highlight_language
                )
            except AttributeError:
                pass
        if not language and default_language:
            language = self.config.get("highlight_language", "")
        node = nodes.literal_block(text, text, language=language)
        self.current_node.append(node)

    def render_inline_code(self, token):
        text = token.children[0].content
        node = nodes.literal(text, text)
        self.current_node.append(node)

    def _is_section_level(self, level, section):
        return self._level_to_elem.get(level, None) == section

    def _add_section(self, section, level):
        parent_level = max(
            section_level
            for section_level in self._level_to_elem
            if level > section_level
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

    def render_heading(self, token):
        # Test if we're replacing a section level first
        if isinstance(self.current_node, nodes.section):
            if self._is_section_level(token.level, self.current_node):
                self.current_node = self.current_node.parent

        title_node = nodes.title()
        title_node.line = token.range[0]

        new_section = nodes.section()
        new_section.line = token.range[0]
        new_section.append(title_node)

        self._add_section(new_section, token.level)

        self.current_node = title_node
        self.render_children(token)

        assert isinstance(self.current_node, nodes.title)
        text = self.current_node.astext()
        # if self.translate_section_name:
        #     text = self.translate_section_name(text)
        name = nodes.fully_normalize_name(text)
        section = self.current_node.parent
        section["names"].append(name)
        self.document.note_implicit_target(section, section)
        self.current_node = section

    def handle_cross_reference(self, token, destination, ref_node):
        # TODO use the docutils error reporting mechanisms, rather than raising
        raise NotImplementedError(
            "reference not found in current document: {}".format(destination)
        )

    def render_link(self, token):
        ref_node = nodes.reference()
        # Check destination is supported for cross-linking and remove extension
        # TODO escape urls?
        destination = token.target
        _, ext = splitext(destination)
        # TODO check for other supported extensions, such as those specified in
        # the Sphinx conf.py file but how to access this information?
        # TODO this should probably only remove the extension for local paths,
        # i.e. not uri's starting with http or other external prefix.

        # if ext.replace('.', '') in self.supported:
        #     destination = destination.replace(ext, '')
        ref_node["refuri"] = destination
        # TODO get line of Link token (requires upstream mistletoe improvements)
        # ref_node.line = self._get_line(token)
        if token.title:
            ref_node["title"] = token.title
        next_node = ref_node

        url_check = urlparse(destination)
        # If there's not a url scheme (e.g. 'https' for 'https:...' links),
        # or there is a scheme but it's not in the list of known_url_schemes,
        # then assume it's a cross-reference
        known_url_schemes = self.config.get("known_url_schemes", None)
        if known_url_schemes:
            scheme_known = url_check.scheme in known_url_schemes
        else:
            scheme_known = bool(url_check.scheme)

        if not url_check.fragment and not scheme_known:
            next_node = self.handle_cross_reference(token, destination, ref_node)

        self.current_node.append(next_node)
        with self.set_current_node(ref_node):
            self.render_children(token)

    def render_image(self, token):
        img_node = nodes.image()
        img_node["uri"] = token.src

        img_node["alt"] = ""
        if token.children and isinstance(token.children[0], myst_span_tokens.RawText):
            img_node["alt"] = token.children[0].content
            token.children[0].content = ""

        self.current_node.append(img_node)
        # TODO how should non-raw alternative text be handled?
        # with self.set_current_node(img_node):
        #     self.render_children(token)

    def render_list(self, token):
        list_node = None
        if token.start is not None:
            list_node = nodes.enumerated_list()
            # TODO deal with token.start?
            # TODO support numerals/letters for lists
            # (see https://stackoverflow.com/a/48372856/5033292)
            # See docutils/docutils/parsers/rst/states.py:Body.enumerator
            # list_node['enumtype'] = 'arabic', 'loweralpha', 'upperroman', etc.
            # list_node['start']
            # list_node['prefix']
            # list_node['suffix']
        else:
            list_node = nodes.bullet_list()
        # TODO deal with token.loose?
        # TODO list range
        # list_node.line = token.range[0]

        self.current_node.append(list_node)
        with self.set_current_node(list_node):
            self.render_children(token)

    def render_list_item(self, token: myst_block_tokens.ListItem):
        item_node = nodes.list_item()
        # TODO list item range
        # node.line = token.range[0]
        self.current_node.append(item_node)
        with self.set_current_node(item_node):
            self.render_children(token)

    def render_table(self, token):
        table = nodes.table()
        table["classes"] += ["colwidths-auto"]
        # TODO column alignment
        maxcols = max(len(c.children) for c in token.children)
        # TODO are colwidths actually required
        colwidths = [100 / maxcols] * maxcols
        tgroup = nodes.tgroup(cols=len(colwidths))
        table += tgroup
        for colwidth in colwidths:
            colspec = nodes.colspec(colwidth=colwidth)
            tgroup += colspec

        if hasattr(token, "header"):
            thead = nodes.thead()
            tgroup += thead
            with self.set_current_node(thead):
                self.render_table_row(token.header)

        tbody = nodes.tbody()
        tgroup += tbody

        with self.set_current_node(tbody):
            self.render_children(token)

        self.current_node.append(table)

    def render_table_row(self, token):
        row = nodes.row()
        with self.set_current_node(row, append=True):
            self.render_children(token)

    def render_table_cell(self, token):
        entry = nodes.entry()
        with self.set_current_node(entry, append=True):
            self.render_children(token)

    def render_auto_link(self, token):
        if token.mailto:
            refuri = "mailto:{}".format(token.target)
        else:
            refuri = escape_url(token.target)
        ref_node = nodes.reference(token.target, token.target, refuri=refuri)
        self.current_node.append(ref_node)

    def render_html_span(self, token):
        self.current_node.append(nodes.raw("", token.content, format="html"))

    def render_html_block(self, token):
        self.current_node.append(nodes.raw("", token.content, format="html"))

    def render_role(self, token):
        content = token.children[0].content
        name = token.name
        # TODO role name white/black lists
        lineno = 0  # TODO get line number
        inliner = MockInliner(self, lineno)
        role_func, messages = roles.role(
            name, self.language_module, lineno, self.document.reporter
        )
        rawsource = ":{}:`{}`".format(name, content)
        # # backslash escapes converted to nulls (``\x00``)
        text = span_token.EscapeSequence.strip(content)
        if role_func:
            nodes, messages2 = role_func(name, rawsource, text, lineno, inliner)
            # return nodes, messages + messages2
            self.current_node += nodes
        else:
            message = self.document.reporter.error(
                'Unknown interpreted text role "{}".'.format(name), line=lineno
            )
            # return ([self.problematic(content, content, msg)], messages + [msg])
            problematic = inliner.problematic(text, rawsource, message)
            self.current_node += problematic

    def render_directive(self, token):
        """parse fenced code blocks as directives.

        Such a fenced code block starts with `{directive_name}`,
        followed by arguments on the same line.

        Directive options are read from a YAML block,
        if the first content line starts with `---`, e.g.

        ::

            ```{directive_name} arguments
            ---
            option1: name
            option2: |
                Longer text block
            ---
            content...
            ```

        Or the option block will be parsed if the first content line starts with `:`,
        as a YAML block consisting of every line that starts with a `:`, e.g.

        ::

            ```{directive_name} arguments
            :option1: name
            :option2: other

            content...
            ```

        If the first line of a directive's content is blank, this will be stripped
        from the content.
        This is to allow for separation between the option block and content.

        """
        name = token.language[1:-1]
        content = token.children[0].content
        options = {}
        # get YAML options
        if content.startswith("---"):
            content = "\n".join(content.splitlines()[1:])
            match = re.search(r"^-{3,}", content, re.MULTILINE)
            if match:
                yaml_block = content[: match.start()]
                content = content[match.end() + 1 :]  # TODO advance line number
            else:
                yaml_block = content
                content = ""
            try:
                yaml_block = dedent(yaml_block)
                options = yaml.safe_load(yaml_block) or {}
            except (yaml.parser.ParserError, yaml.scanner.ScannerError) as error:
                msg_node = self.document.reporter.system_message(
                    3, "Directive options:\n" + str(error), line=token.range[0]
                )  # 3 is ERROR level
                msg_node += nodes.literal_block(yaml_block, yaml_block)
                self.current_node += [msg_node]
                return
            # TODO check options are an un-nested dict / json serialize ?
        elif content.startswith(":"):
            content_lines = content.splitlines()  # type: list
            yaml_lines = []
            while content_lines:
                if not content_lines[0].startswith(":"):
                    break
                yaml_lines.append(content_lines.pop(0)[1:].lstrip())
            yaml_block = "\n".join(yaml_lines)
            content = "\n".join(content_lines)
            try:
                options = yaml.safe_load(yaml_block) or {}
            except (yaml.parser.ParserError, yaml.scanner.ScannerError) as error:
                msg_node = self.document.reporter.system_message(
                    3, "Directive options:\n" + str(error), line=token.range[0]
                )  # 3 is ERROR level
                msg_node += nodes.literal_block(yaml_block, yaml_block)
                self.current_node += [msg_node]
                return

        # remove first line if blank
        content_lines = content.splitlines()
        if content_lines and not content_lines[0].strip():
            content_lines = content_lines[1:]

        # TODO directive name white/black lists
        directive_class, messages = directives.directive(
            name, self.language_module, self.document
        )
        if not directive_class:
            # TODO deal with unknown directive
            self.current_node += messages
            return

        try:
            arguments = self.parse_directive_arguments(directive_class, token.arguments)
        except RuntimeError:
            # TODO handle/report error
            raise

        state_machine = MockStateMachine(self, token.range[0])

        directive_instance = directive_class(
            name=name,
            # the list of positional arguments
            arguments=arguments,
            # a dictionary mapping option names to values
            # TODO option parsing
            options=options,
            # the directive content line by line
            content=content_lines,
            # the absolute line number of the first line of the directive
            lineno=token.range[0],
            # the line offset of the first line of the content
            content_offset=0,
            # a string containing the entire directive
            block_text="\n".join(content_lines),
            state=MockState(self, state_machine, token.range[0]),
            state_machine=state_machine,
        )

        try:
            result = directive_instance.run()
        except DirectiveError as error:
            msg_node = self.document.reporter.system_message(
                error.level, error.msg, line=token.range[0]
            )
            msg_node += nodes.literal_block(content, content)
            result = [msg_node]
        except (AttributeError, NotImplementedError):
            # TODO deal with directives that call unimplemented methods of State/Machine
            raise
        assert isinstance(
            result, list
        ), 'Directive "{}" must return a list of nodes.'.format(name)
        for i in range(len(result)):
            assert isinstance(
                result[i], nodes.Node
            ), 'Directive "{}" returned non-Node object (index {}): {}'.format(
                name, i, result[i]
            )
        self.current_node += result

    @staticmethod
    def parse_directive_arguments(directive, arg_text):
        required = directive.required_arguments
        optional = directive.optional_arguments
        arguments = arg_text.split()
        if len(arguments) < required:
            raise RuntimeError(
                "{} argument(s) required, {} supplied".format(required, len(arguments))
            )
        elif len(arguments) > required + optional:
            if directive.final_argument_whitespace:
                arguments = arg_text.split(None, required + optional - 1)
            else:
                raise RuntimeError(
                    "maximum {} argument(s) allowed, {} supplied".format(
                        required + optional, len(arguments)
                    )
                )
        return arguments


class SphinxRenderer(DocutilsRenderer):
    """A mistletoe renderer to populate (in-place) a `docutils.document` AST.

    This is sub-class of `DocutilsRenderer` that handles sphinx cross-referencing.
    """

    def handle_cross_reference(self, token, destination, ref_node):
        from sphinx import addnodes

        wrap_node = addnodes.pending_xref(
            reftarget=unquote(destination),
            reftype="any",
            refdomain=None,  # Added to enable cross-linking
            refexplicit=True,
            refwarn=True,
        )
        # TODO also not correct sourcepos
        # wrap_node.line = self._get_line(token)
        if token.title:
            wrap_node["title"] = token.title
        wrap_node.append(ref_node)
        return wrap_node

    def mock_sphinx_env(self):
        """Load sphinx roles, directives, etc."""
        from sphinx.application import builtin_extensions, Sphinx
        from sphinx.config import Config
        from sphinx.environment import BuildEnvironment
        from sphinx.events import EventManager
        from sphinx.project import Project
        from sphinx.registry import SphinxComponentRegistry

        class MockSphinx(Sphinx):
            def __init__(self):
                self.registry = SphinxComponentRegistry()
                self.config = Config({}, {})
                self.events = EventManager(self)
                self.html_themes = {}
                self.extensions = {}
                for extension in builtin_extensions:
                    self.registry.load_extension(self, extension)
                # fresh env
                self.doctreedir = "/doctreedir/"
                self.srcdir = "/srcdir/"
                self.project = Project(srcdir="", source_suffix=".md")
                self.project.docnames = ["mock_docname"]
                self.env = BuildEnvironment()
                self.env.setup(self)
                self.env.temp_data["docname"] = "mock_docname"

        app = MockSphinx()
        self.document.settings.env = app.env
        return app


class MockInliner:
    """A mock version of `docutils.parsers.rst.states.Inliner`.

    This is parsed to role functions.
    """

    def __init__(self, renderer: DocutilsRenderer, lineno: int):
        self._renderer = renderer
        self.document = renderer.document
        self.reporter = renderer.document.reporter
        if not hasattr(self.reporter, "get_source_and_line"):
            # TODO this is called by some roles,
            # but I can't see how that would work in RST?
            self.reporter.get_source_and_line = mock.Mock(
                return_value=(self.document.source, lineno)
            )
        self.parent = renderer.current_node
        self.language = renderer.language_module
        self.rfc_url = "rfc%d.html"

    def problematic(self, text: str, rawsource: str, message: nodes.system_message):
        msgid = self.document.set_id(message, self.parent)
        problematic = nodes.problematic(rawsource, rawsource, refid=msgid)
        prbid = self.document.set_id(problematic)
        message.add_backref(prbid)
        return problematic

    # TODO add parse method

    def __getattr__(self, name):
        """This method is only be called if the attribute requested has not
        been defined. Defined attributes will not be overridden.
        """
        # TODO use document.reporter mechanism?
        if hasattr(Inliner, name):
            msg = "{cls} has not yet implemented attribute {name}".format(
                cls=type(self).__name__, name=name
            )
            raise NotImplementedError(msg).with_traceback(sys.exc_info()[2])
        msg = "{cls} has no attribute {name}".format(cls=type(self).__name__, name=name)
        raise AttributeError(msg).with_traceback(sys.exc_info()[2])


class MockState:
    """A mock version of `docutils.parsers.rst.states.RSTState`.

    This is parsed to the `Directives.run()` method,
    so that they may run nested parses on their content that will be parsed as markdown,
    rather than RST.
    """

    def __init__(
        self, renderer: DocutilsRenderer, state_machine: "MockStateMachine", lineno: int
    ):
        self._renderer = renderer
        self._lineno = lineno
        self.document = renderer.document
        self.state_machine = state_machine

        class Struct:
            document = self.document
            reporter = self.document.reporter
            language = self.document.settings.language_code
            title_styles = []
            section_level = max(renderer._level_to_elem)
            section_bubble_up_kludge = False
            inliner = MockInliner(renderer, lineno)

        self.memo = Struct

    def nested_parse(
        self,
        block: List[str],
        input_offset: int,
        node: nodes.Element,
        match_titles: bool = False,
        state_machine_class=None,
        state_machine_kwargs=None,
    ):
        current_match_titles = self.state_machine.match_titles
        self.state_machine.match_titles = match_titles
        nested_renderer = self._renderer.__class__(
            document=self.document, current_node=node
        )
        self.state_machine.match_titles = current_match_titles
        # TODO deal with starting line number
        nested_renderer.render(Document(block))

    def inline_text(self, text: str, lineno: int):
        # TODO return messages?
        messages = []
        paragraph = nodes.paragraph("")
        renderer = self._renderer.__class__(
            document=self.document, current_node=paragraph
        )
        renderer.render(Document(text))
        textnodes = []
        if paragraph.children:
            # first child should be paragraph
            textnodes = paragraph.children[0].children
        return textnodes, messages

    # U+2014 is an em-dash:
    attribution_pattern = re.compile("^((?:---?(?!-)|\u2014) *)(.+)")

    def block_quote(self, lines: List[str], line_offset: int):
        """Parse a block quote, which is a block of text,
        followed by an (optional) attribution.

        ::

           No matter where you go, there you are.

           -- Buckaroo Banzai
        """
        elements = []
        # split attribution
        last_line_blank = False
        blockquote_lines = lines
        attribution_lines = []
        attribution_line_offset = None
        # First line after a blank line must begin with a dash
        for i, line in enumerate(lines):
            if not line.strip():
                last_line_blank = True
                continue
            if not last_line_blank:
                last_line_blank = False
                continue
            last_line_blank = False
            match = self.attribution_pattern.match(line)
            if not match:
                continue
            attribution_line_offset = i
            attribution_lines = [match.group(2)]
            for at_line in lines[i + 1 :]:
                indented_line = at_line[len(match.group(1)) :]
                if len(indented_line) != len(at_line.lstrip()):
                    break
                attribution_lines.append(indented_line)
            blockquote_lines = lines[:i]
            break
        # parse block
        blockquote = nodes.block_quote()
        self.nested_parse(blockquote_lines, line_offset, blockquote)
        elements.append(blockquote)
        # parse attribution
        if attribution_lines:
            attribution_text = "\n".join(attribution_lines)
            lineno = self._lineno + line_offset + attribution_line_offset
            textnodes, messages = self.inline_text(attribution_text, lineno)
            attribution = nodes.attribution(attribution_text, "", *textnodes)
            (
                attribution.source,
                attribution.line,
            ) = self.state_machine.get_source_and_line(lineno)
            blockquote += attribution
            elements += messages
        return elements

    def __getattr__(self, name):
        """This method is only be called if the attribute requested has not
        been defined. Defined attributes will not be overridden.
        """
        # TODO use document.reporter mechanism?
        if hasattr(Body, name):
            msg = "{cls} has not yet implemented attribute {name}".format(
                cls=type(self).__name__, name=name
            )
            raise NotImplementedError(msg).with_traceback(sys.exc_info()[2])
        msg = "{cls} has no attribute {name}".format(cls=type(self).__name__, name=name)
        raise AttributeError(msg).with_traceback(sys.exc_info()[2])


class MockStateMachine:
    """A mock version of `docutils.parsers.rst.states.RSTStateMachine`.

    This is parsed to the `Directives.run()` method.
    """

    def __init__(self, renderer: DocutilsRenderer, lineno: int):
        self._renderer = renderer
        self._lineno = lineno
        self.document = renderer.document
        self.reporter = self.document.reporter
        self.node = renderer.current_node
        self.match_titles = True

    def get_source_and_line(self, lineno: Optional[int] = None):
        """Return (source, line) tuple for current or given line number."""
        # TODO return correct line source
        return "", lineno or self._lineno

    def __getattr__(self, name):
        """This method is only be called if the attribute requested has not
        been defined. Defined attributes will not be overridden.
        """
        # TODO use document.reporter mechanism?
        if hasattr(RSTStateMachine, name):
            msg = "{cls} has not yet implemented attribute {name}".format(
                cls=type(self).__name__, name=name
            )
            raise NotImplementedError(msg).with_traceback(sys.exc_info()[2])
        msg = "{cls} has no attribute {name}".format(cls=type(self).__name__, name=name)
        raise AttributeError(msg).with_traceback(sys.exc_info()[2])
