from contextlib import contextmanager
import copy
from os.path import splitext
from pathlib import Path
import re
import sys
from typing import List, Optional
from urllib.parse import urlparse, unquote

from docutils import nodes
from docutils.frontend import OptionParser
from docutils.languages import get_language
from docutils.parsers.rst import directives, Directive, DirectiveError, roles
from docutils.parsers.rst import Parser as RSTParser
from docutils.parsers.rst.directives.misc import Include
from docutils.parsers.rst.states import RSTStateMachine, Body, Inliner
from docutils.statemachine import StringList
from docutils.utils import new_document, Reporter
import yaml

from mistletoe import block_tokens, block_tokens_ext, span_tokens, span_tokens_ext
from mistletoe.renderers.base import BaseRenderer

from myst_parser import block_tokens as myst_block_tokens
from myst_parser import span_tokens as myst_span_tokens
from myst_parser.parse_directives import parse_directive_text, DirectiveParsingError
from myst_parser.utils import escape_url


class DocutilsRenderer(BaseRenderer):
    """A mistletoe renderer to populate (in-place) a `docutils.document` AST.

    Note this renderer has no dependencies on Sphinx.
    """

    default_block_tokens = (
        block_tokens.HTMLBlock,
        myst_block_tokens.LineComment,
        block_tokens.BlockCode,
        block_tokens.Heading,
        myst_block_tokens.Quote,
        block_tokens.CodeFence,
        block_tokens.ThematicBreak,
        myst_block_tokens.BlockBreak,
        myst_block_tokens.List,
        block_tokens_ext.Table,
        block_tokens.LinkDefinition,
        myst_block_tokens.Paragraph,
    )

    default_span_tokens = (
        span_tokens.EscapeSequence,
        myst_span_tokens.Role,
        span_tokens.HTMLSpan,
        span_tokens.AutoLink,
        myst_span_tokens.Target,
        span_tokens.CoreTokens,
        span_tokens_ext.Math,
        # TODO there is no matching core element in docutils for strikethrough
        # span_tokens_ext.Strikethrough,
        span_tokens.InlineCode,
        span_tokens.LineBreak,
        span_tokens.RawText,
    )

    def __init__(
        self,
        document: Optional[nodes.document] = None,
        current_node: Optional[nodes.Element] = None,
        config: Optional[dict] = None,
        find_blocks=None,
        find_spans=None,
    ):
        """Initialise the renderer.

        :param document: The document to populate (or create a new one if None)
        :param current_node: The root node from which to begin populating
            (default is document, or should be an ancestor of document)
        :param config: contains configuration specific to the rendering process
        :param find_blocks: override the default block tokens (classes or class paths)
        :param find_spans: override the default span tokens (classes or class paths)
        """
        self.config = config or {}
        self.document = document or self.new_document()  # type: nodes.document
        self.reporter = self.document.reporter  # type: Reporter
        self.current_node = current_node or self.document  # type: nodes.Element
        self.language_module = self.document.settings.language_code  # type: str
        get_language(self.language_module)
        self._level_to_elem = {0: self.document}

        super().__init__(find_blocks=find_blocks, find_spans=find_spans)

    def new_document(self, source_path="notset") -> nodes.document:
        settings = OptionParser(components=(RSTParser,)).get_default_values()
        return new_document(source_path, settings=settings)

    def add_line_and_source_path(self, node, token):
        """Copy the line number and document source path to the docutils node."""
        try:
            node.line = token.position[0] + 1
        except (AttributeError, TypeError):
            pass
        node.source = self.document["source"]

    def nested_render_text(self, text: str, lineno: int):
        """Render unparsed text."""
        token = myst_block_tokens.Document.read(
            text, start_line=lineno, front_matter=True
        )
        # TODO think if this is the best way: here we consume front matter,
        # but then remove it. this is for example if includes have front matter
        token.front_matter = None
        self.render(token)

    def render_children(self, token):
        for child in token.children:
            self.render(child)

    @contextmanager
    def current_node_context(self, node, append: bool = False):
        """Context manager for temporarily setting the current node."""
        if append:
            self.current_node.append(node)
        current_node = self.current_node
        self.current_node = node
        yield
        self.current_node = current_node

    def render_document(self, token):
        self.link_definitions.update(token.link_definitions)
        if token.front_matter:
            self.render_front_matter(token.front_matter)
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
        try:
            data = yaml.safe_load(token.content) or {}
        except (yaml.parser.ParserError, yaml.scanner.ScannerError) as error:
            msg_node = self.reporter.error(
                "Front matter block:\n" + str(error), line=token.position[0]
            )
            msg_node += nodes.literal_block(token.content, token.content)
            self.current_node += [msg_node]
            return

        docinfo = dict_to_docinfo(data)
        self.current_node.append(docinfo)

    def render_paragraph(self, token):
        if len(token.children) == 1 and isinstance(
            token.children[0], myst_span_tokens.Target
        ):
            # promote the target to block level
            return self.render_target(token.children[0])
        para = nodes.paragraph("")
        self.add_line_and_source_path(para, token)
        with self.current_node_context(para, append=True):
            self.render_children(token)

    def render_line_comment(self, token):
        self.current_node.append(nodes.comment(token.content, token.content))

    def render_target(self, token):
        text = token.children[0].content
        name = nodes.fully_normalize_name(text)
        target = nodes.target(text)
        target["names"].append(name)
        self.add_line_and_source_path(target, token)
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
        self.add_line_and_source_path(node, token)
        with self.current_node_context(node, append=True):
            self.render_children(token)

    def render_emphasis(self, token):
        node = nodes.emphasis()
        self.add_line_and_source_path(node, token)
        with self.current_node_context(node, append=True):
            self.render_children(token)

    def render_quote(self, token):
        quote = nodes.block_quote()
        self.add_line_and_source_path(quote, token)
        with self.current_node_context(quote, append=True):
            self.render_children(token)

    def render_strikethrough(self, token):
        # TODO there is no existing node/role for this
        raise NotImplementedError

    def render_thematic_break(self, token):
        node = nodes.transition()
        self.add_line_and_source_path(node, token)
        self.current_node.append(node)

    def render_block_break(self, token):
        block_break = nodes.comment(token.content, token.content)
        block_break["classes"] += ["block_break"]
        self.add_line_and_source_path(block_break, token)
        self.current_node.append(block_break)

    def render_math(self, token):
        if token.content.startswith("$$"):
            content = token.content[2:-2]
            node = nodes.math_block(content, content, nowrap=False, number=None)
        else:
            content = token.content[1:-1]
            node = nodes.math(content, content)
        self.add_line_and_source_path(node, token)
        self.current_node.append(node)

    def render_block_code(self, token):
        # this should never have a language, since it is just indented text, however,
        # creating a literal_block with no language will raise a warning in sphinx
        text = token.children[0].content
        language = token.language or "none"
        node = nodes.literal_block(text, text, language=language)
        self.add_line_and_source_path(node, token)
        self.current_node.append(node)

    def render_code_fence(self, token):
        if token.language.startswith("{") and token.language.endswith("}"):
            return self.render_directive(token)

        text = token.children[0].content
        language = token.language
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

    def render_inline_code(self, token):
        text = token.children[0].content
        node = nodes.literal(text, text)
        self.add_line_and_source_path(node, token)
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
        self.add_line_and_source_path(title_node, token)

        new_section = nodes.section()
        self.add_line_and_source_path(new_section, token)
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

    def handle_cross_reference(self, token, destination):
        # TODO use the docutils error reporting mechanisms, rather than raising
        if not self.config.get("ignore_missing_refs", False):
            raise NotImplementedError(
                "reference not found in current document: {}\n{}".format(
                    destination, token
                )
            )

    def render_link(self, token):
        ref_node = nodes.reference()
        self.add_line_and_source_path(ref_node, token)
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
            self.handle_cross_reference(token, destination)
        else:
            self.current_node.append(next_node)
            with self.current_node_context(ref_node):
                self.render_children(token)

    def render_image(self, token):
        img_node = nodes.image()
        self.add_line_and_source_path(img_node, token)
        img_node["uri"] = token.src

        img_node["alt"] = ""
        if token.children and isinstance(token.children[0], span_tokens.RawText):
            img_node["alt"] = token.children[0].content
            token.children[0].content = ""

        self.current_node.append(img_node)
        # TODO how should non-raw alternative text be handled?
        # with self.set_current_node(img_node):
        #     self.render_children(token)

    def render_list(self, token):
        list_node = None
        if token.start_at is not None:
            list_node = nodes.enumerated_list()
            # TODO deal with token.start_at?
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
        self.add_line_and_source_path(list_node, token)

        self.current_node.append(list_node)
        with self.current_node_context(list_node):
            self.render_children(token)

    def render_list_item(self, token: myst_block_tokens.ListItem):
        item_node = nodes.list_item()
        self.add_line_and_source_path(item_node, token)
        self.current_node.append(item_node)
        with self.current_node_context(item_node):
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
            with self.current_node_context(thead):
                self.render_table_row(token.header)

        tbody = nodes.tbody()
        tgroup += tbody

        with self.current_node_context(tbody):
            self.render_children(token)

        self.current_node.append(table)

    def render_table_row(self, token):
        row = nodes.row()
        with self.current_node_context(row, append=True):
            self.render_children(token)

    def render_table_cell(self, token):
        entry = nodes.entry()
        with self.current_node_context(entry, append=True):
            self.render_children(token)

    def render_auto_link(self, token):
        if token.mailto:
            refuri = "mailto:{}".format(token.target)
        else:
            refuri = escape_url(token.target)
        ref_node = nodes.reference(token.target, token.target, refuri=refuri)
        self.add_line_and_source_path(ref_node, token)
        self.current_node.append(ref_node)

    def render_html_span(self, token):
        self.current_node.append(nodes.raw("", token.content, format="html"))

    def render_html_block(self, token):
        self.current_node.append(nodes.raw("", token.content, format="html"))

    def render_role(self, token):
        content = token.children[0].content
        name = token.role_name
        # TODO role name white/black lists
        try:
            lineno = token.position[0]
        except (AttributeError, TypeError):
            lineno = 0
        inliner = MockInliner(self, lineno)
        role_func, messages = roles.role(
            name, self.language_module, lineno, self.reporter
        )
        rawsource = ":{}:`{}`".format(name, content)
        # # backslash escapes converted to nulls (``\x00``)
        text = span_tokens.EscapeSequence.strip(content)
        if role_func:
            nodes, messages2 = role_func(name, rawsource, text, lineno, inliner)
            # return nodes, messages + messages2
            self.current_node += nodes
        else:
            message = self.reporter.error(
                'Unknown interpreted text role "{}".'.format(name), line=lineno
            )
            # return ([self.problematic(content, content, msg)], messages + [msg])
            problematic = inliner.problematic(text, rawsource, message)
            self.current_node += problematic

    def render_directive(self, token):
        """Render special fenced code blocks as directives."""
        name = token.language[1:-1]
        # TODO directive name white/black lists
        content = token.children[0].content
        self.document.current_line = token.position[0]

        # get directive class
        directive_class, messages = directives.directive(
            name, self.language_module, self.document
        )  # type: (Directive, list)
        if not directive_class:
            error = self.reporter.error(
                "Unknown directive type '{}'\n".format(name),
                # nodes.literal_block(content, content),
                line=token.position[0],
            )
            self.current_node += [error] + messages
            return

        try:
            arguments, options, body_lines = parse_directive_text(
                directive_class, token.arguments, content
            )
        except DirectiveParsingError as error:
            error = self.reporter.error(
                "Directive '{}':\n{}".format(name, error),
                nodes.literal_block(content, content),
                line=token.position[0],
            )
            self.current_node += [error]
            return

        # initialise directive
        if issubclass(directive_class, Include):
            directive_instance = MockIncludeDirective(
                self,
                name=name,
                klass=directive_class,
                arguments=arguments,
                options=options,
                body=body_lines,
                lineno=token.position[0],
            )
        else:
            state_machine = MockStateMachine(self, token.position[0])
            state = MockState(self, state_machine, token.position[0])
            directive_instance = directive_class(
                name=name,
                # the list of positional arguments
                arguments=arguments,
                # a dictionary mapping option names to values
                options=options,
                # the directive content line by line
                content=StringList(body_lines, self.document["source"]),
                # the absolute line number of the first line of the directive
                lineno=token.position[0],
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
                error.level, error.msg, line=token.position[0]
            )
            msg_node += nodes.literal_block(content, content)
            result = [msg_node]
        except MockingError as exc:
            error = self.reporter.error(
                "Directive '{}' cannot be mocked:\n{}: {}".format(
                    name, exc.__class__.__name__, exc
                ),
                nodes.literal_block(content, content),
                line=token.position[0],
            )
            self.current_node += [error]
            return
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


class SphinxRenderer(DocutilsRenderer):
    """A mistletoe renderer to populate (in-place) a `docutils.document` AST.

    This is sub-class of `DocutilsRenderer` that handles sphinx cross-referencing.
    """

    def __init__(self, *args, **kwargs):
        """Intitalise SphinxRenderer

        :param load_sphinx_env: load a basic sphinx environment,
            when using the renderer as a context manager outside if `sphinx-build`
        :param sphinx_conf: a dictionary representation of the sphinx `conf.py`
        :param sphinx_srcdir: a path to a source directory
          (for example, can be used for `include` statements)

        To use this renderer in a 'standalone' fashion::

            from myst_parser.block_tokens import Document

            with SphinxRenderer(load_sphinx_env=True, sphinx_conf={}) as renderer:
                renderer.render(Document.read("source text"))

        """
        self.load_sphinx_env = kwargs.pop("load_sphinx_env", False)
        self.sphinx_conf = kwargs.pop("sphinx_conf", None)
        self.sphinx_srcdir = kwargs.pop("sphinx_srcdir", None)
        super().__init__(*args, **kwargs)

    def handle_cross_reference(self, token, destination):
        from sphinx import addnodes

        wrap_node = addnodes.pending_xref(
            reftarget=unquote(destination),
            reftype="any",
            refdomain=None,  # Added to enable cross-linking
            refexplicit=len(token.children) > 0,
            refwarn=True,
        )
        self.add_line_and_source_path(wrap_node, token)
        if token.title:
            wrap_node["title"] = token.title
        self.current_node.append(wrap_node)
        text_node = nodes.literal("", "", classes=["xref", "any"])
        wrap_node.append(text_node)
        with self.current_node_context(text_node):
            self.render_children(token)

    def mock_sphinx_env(self, configuration=None, sourcedir=None):
        """Load sphinx roles, directives, etc."""
        from sphinx.application import builtin_extensions, Sphinx
        from sphinx.config import Config
        from sphinx.environment import BuildEnvironment
        from sphinx.events import EventManager
        from sphinx.project import Project
        from sphinx.registry import SphinxComponentRegistry
        from sphinx.util.tags import Tags

        class MockSphinx(Sphinx):
            """Minimal sphinx init to load roles and directives."""

            def __init__(self, confoverrides=None, srcdir=None):
                self.extensions = {}
                self.registry = SphinxComponentRegistry()
                self.html_themes = {}
                self.events = EventManager(self)
                self.tags = Tags(None)
                self.config = Config({}, confoverrides or {})
                self.config.pre_init_values()
                self._init_i18n()
                for extension in builtin_extensions:
                    self.registry.load_extension(self, extension)
                # fresh env
                self.doctreedir = None
                self.srcdir = srcdir
                self.confdir = None
                self.outdir = None
                self.project = Project(srcdir=srcdir, source_suffix=".md")
                self.project.docnames = ["mock_docname"]
                self.env = BuildEnvironment()
                self.env.setup(self)
                self.env.temp_data["docname"] = "mock_docname"
                self.builder = None

                if not confoverrides:
                    return

                # this code is only required for more complex parsing with extensions
                for extension in self.config.extensions:
                    self.setup_extension(extension)
                buildername = "dummy"
                self.preload_builder(buildername)
                self.config.init_values()
                self.events.emit("config-inited", self.config)
                import tempfile

                with tempfile.TemporaryDirectory() as tempdir:
                    # creating a builder attempts to make the doctreedir
                    self.doctreedir = tempdir
                    self.builder = self.create_builder(buildername)
                self.doctreedir = None

        app = MockSphinx(confoverrides=configuration, srcdir=sourcedir)
        self.document.settings.env = app.env
        return app

    def __enter__(self):
        """If `load_sphinx_env=True`, we set up an environment,
        to parse sphinx roles/directives, outside of a `sphinx-build`.

        This primarily copies the code in `sphinx.util.docutils.docutils_namespace`
        and `sphinx.util.docutils.sphinx_domains`.
        """
        if not self.load_sphinx_env:
            return super().__enter__()

        # store currently loaded roles/directives, so we can revert on exit
        self._directives = copy.copy(directives._directives)
        self._roles = copy.copy(roles._roles)
        # Monkey-patch directive and role dispatch,
        # so that sphinx domain-specific markup takes precedence.
        self._env = self.mock_sphinx_env(
            configuration=self.sphinx_conf, sourcedir=self.sphinx_srcdir
        ).env
        from sphinx.util.docutils import sphinx_domains

        self._sphinx_domains = sphinx_domains(self._env)
        self._sphinx_domains.enable()

        return super().__enter__()

    def __exit__(self, exception_type, exception_val, traceback):
        if not self.load_sphinx_env:
            return super().__exit__(exception_type, exception_val, traceback)
        # revert loaded roles/directives
        directives._directives = self._directives
        roles._roles = self._roles
        self._directives = None
        self._roles = None
        # unregister nodes (see `sphinx.util.docutils.docutils_namespace`)
        from sphinx.util.docutils import additional_nodes, unregister_node

        for node in list(additional_nodes):
            unregister_node(node)
            additional_nodes.discard(node)
        # revert directive/role function (see `sphinx.util.docutils.sphinx_domains`)
        self._sphinx_domains.disable()
        self._sphinx_domains = None
        self._env = None
        return super().__exit__(exception_type, exception_val, traceback)


class MockingError(Exception):
    """An exception to signal an error during mocking of docutils components."""


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
            self.reporter.get_source_and_line = lambda l: (self.document["source"], l)
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
            msg = "{cls} has not yet implemented attribute '{name}'".format(
                cls=type(self).__name__, name=name
            )
            raise MockingError(msg).with_traceback(sys.exc_info()[2])
        msg = "{cls} has no attribute {name}".format(cls=type(self).__name__, name=name)
        raise MockingError(msg).with_traceback(sys.exc_info()[2])


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
        block: StringList,
        input_offset: int,
        node: nodes.Element,
        match_titles: bool = False,
        state_machine_class=None,
        state_machine_kwargs=None,
    ):
        current_match_titles = self.state_machine.match_titles
        self.state_machine.match_titles = match_titles
        with self._renderer.current_node_context(node):
            self._renderer.nested_render_text(block, self._lineno + input_offset)
        self.state_machine.match_titles = current_match_titles

    def inline_text(self, text: str, lineno: int):
        # TODO return messages?
        messages = []
        paragraph = nodes.paragraph("")
        renderer = self._renderer.__class__(
            document=self.document, current_node=paragraph
        )
        renderer.render(
            myst_block_tokens.Document.read(
                text, start_line=self._lineno, front_matter=False
            )
        )
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

    def build_table(self, tabledata, tableline, stub_columns=0, widths=None):
        return Body.build_table(self, tabledata, tableline, stub_columns, widths)

    def build_table_row(self, rowdata, tableline):
        return Body.build_table_row(self, rowdata, tableline)

    def __getattr__(self, name):
        """This method is only be called if the attribute requested has not
        been defined. Defined attributes will not be overridden.
        """
        if hasattr(Body, name):
            msg = "{cls} has not yet implemented attribute '{name}'".format(
                cls=type(self).__name__, name=name
            )
            raise MockingError(msg).with_traceback(sys.exc_info()[2])
        msg = "{cls} has no attribute {name}".format(cls=type(self).__name__, name=name)
        raise MockingError(msg).with_traceback(sys.exc_info()[2])


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

        # TODO to allow to access like attributes like input_lines,
        # we would need to store the input lines,
        # probably via the `Document` token,
        # and maybe self._lines = lines[:], then for AstRenderer,
        # ignore private attributes

    def get_source(self, lineno: Optional[int] = None):
        """Return document source path."""
        return self.document["source"]

    def get_source_and_line(self, lineno: Optional[int] = None):
        """Return (source path, line) tuple for current or given line number."""
        return self.document["source"], lineno or self._lineno

    def __getattr__(self, name):
        """This method is only be called if the attribute requested has not
        been defined. Defined attributes will not be overridden.
        """
        if hasattr(RSTStateMachine, name):
            msg = "{cls} has not yet implemented attribute '{name}'".format(
                cls=type(self).__name__, name=name
            )
            raise MockingError(msg).with_traceback(sys.exc_info()[2])
        msg = "{cls} has no attribute {name}".format(cls=type(self).__name__, name=name)
        raise MockingError(msg).with_traceback(sys.exc_info()[2])


class MockIncludeDirective:
    """This directive uses a lot of statemachine logic that is not yet mocked.
    Therefore, we treat it as a special case (at least for now).

    See:
    https://docutils.sourceforge.io/docs/ref/rst/directives.html#including-an-external-document-fragment
    """

    def __init__(
        self,
        renderer: DocutilsRenderer,
        name: str,
        klass: Include,
        arguments: list,
        options: dict,
        body: List[str],
        lineno: int,
    ):
        self.renderer = renderer
        self.document = renderer.document
        self.name = name
        self.klass = klass
        self.arguments = arguments
        self.options = options
        self.body = body
        self.lineno = lineno

    def run(self):

        from docutils.parsers.rst.directives.body import CodeBlock, NumberLines

        if not self.document.settings.file_insertion_enabled:
            raise DirectiveError(2, 'Directive "{}" disabled.'.format(self.name))

        source_dir = Path(self.document["source"]).absolute().parent
        include_arg = "".join([s.strip() for s in self.arguments[0].splitlines()])

        if include_arg.startswith("<") and include_arg.endswith(">"):
            # # docutils "standard" includes
            path = Path(self.klass.standard_include_path).joinpath(include_arg[1:-1])
        else:
            # if using sphinx interpret absolute paths "correctly",
            # i.e. relative to source directory
            try:
                sphinx_env = self.document.settings.env
                _, include_arg = sphinx_env.relfn2path(self.arguments[0])
                sphinx_env.note_included(include_arg)
            except AttributeError:
                pass
            path = Path(include_arg)
        path = source_dir.joinpath(path)

        # read file
        encoding = self.options.get("encoding", self.document.settings.input_encoding)
        error_handler = self.document.settings.input_encoding_error_handler
        # tab_width = self.options.get("tab-width", self.document.settings.tab_width)
        try:
            file_content = path.read_text(encoding=encoding, errors=error_handler)
        except Exception as error:
            raise DirectiveError(
                4,
                'Directive "{}": error reading file: {}\n{error}.'.format(
                    self.name, path, error
                ),
            )

        # get required section of text
        startline = self.options.get("start-line", None)
        endline = self.options.get("end-line", None)
        file_content = "\n".join(file_content.splitlines()[startline:endline])
        startline = startline or 0
        for split_on_type in ["start-after", "end-before"]:
            split_on = self.options.get(split_on_type, None)
            if not split_on:
                continue
            split_index = file_content.find(split_on)
            if split_index < 0:
                raise DirectiveError(
                    4,
                    'Directive "{}"; option "{}": text not found "{}".'.format(
                        self.name, split_on_type, split_on
                    ),
                )
            if split_on_type == "start-after":
                startline += split_index + len(split_on)
                file_content = file_content[split_index + len(split_on) :]
            else:
                file_content = file_content[:split_index]

        if "literal" in self.options:
            literal_block = nodes.literal_block(
                file_content, source=str(path), classes=self.options.get("class", [])
            )
            literal_block.line = 1  # TODO don;t think this should be 1?
            self.add_name(literal_block)
            if "number-lines" in self.options:
                try:
                    startline = int(self.options["number-lines"] or 1)
                except ValueError:
                    raise DirectiveError(
                        3, ":number-lines: with non-integer " "start value"
                    )
                endline = startline + len(file_content.splitlines())
                if file_content.endswith("\n"):
                    file_content = file_content[:-1]
                tokens = NumberLines([([], file_content)], startline, endline)
                for classes, value in tokens:
                    if classes:
                        literal_block += nodes.inline(value, value, classes=classes)
                    else:
                        literal_block += nodes.Text(value)
            else:
                literal_block += nodes.Text(file_content)
            return [literal_block]
        if "code" in self.options:
            self.options["source"] = str(path)
            state_machine = MockStateMachine(self.renderer, self.lineno)
            state = MockState(self.renderer, state_machine, self.lineno)
            codeblock = CodeBlock(
                name=self.name,
                arguments=[self.options.pop("code")],
                options=self.options,
                content=file_content.splitlines(),
                lineno=self.lineno,
                content_offset=0,
                block_text=file_content,
                state=state,
                state_machine=state_machine,
            )
            return codeblock.run()

        # Here we perform a nested render, but temporarily setup the document/reporter
        # with the correct document path and lineno for the included file.
        source = self.renderer.document["source"]
        rsource = self.renderer.reporter.source
        line_func = getattr(self.renderer.reporter, "get_source_and_line", None)
        try:
            self.renderer.document["source"] = str(path)
            self.renderer.reporter.source = str(path)
            self.renderer.reporter.get_source_and_line = lambda l: (str(path), l)
            self.renderer.nested_render_text(file_content, startline)
        finally:
            self.renderer.document["source"] = source
            self.renderer.reporter.source = rsource
            if line_func is not None:
                self.renderer.reporter.get_source_and_line = line_func
            else:
                del self.renderer.reporter.get_source_and_line
        return []

    def add_name(self, node):
        """Append self.options['name'] to node['names'] if it exists.

        Also normalize the name string and register it as explicit target.
        """
        if "name" in self.options:
            name = nodes.fully_normalize_name(self.options.pop("name"))
            if "name" in node:
                del node["name"]
            node["names"].append(name)
            self.renderer.document.note_explicit_target(node, node)


def dict_to_docinfo(data):
    """Render a key/val pair as a docutils field node."""
    # TODO this data could be used to support default option values for directives
    docinfo = nodes.docinfo()

    # Throw away all non-stringy values
    # TODO: support more complex data structures as values
    for key, value in data.items():
        if not isinstance(value, (str, int, float)):
            continue
        value = str(value)
        field_node = nodes.field()
        field_node.source = value
        field_node += nodes.field_name(key, "", nodes.Text(key, key))
        field_node += nodes.field_body(value, nodes.Text(value, value))
        docinfo += field_node
    return docinfo
