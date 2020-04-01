from contextlib import contextmanager
import copy
from urllib.parse import unquote
import tempfile
from typing import cast

from docutils import nodes
from docutils.parsers.rst import directives, roles

from sphinx import addnodes
from sphinx.application import builtin_extensions, Sphinx
from sphinx.config import Config
from sphinx.domains.math import MathDomain
from sphinx.environment import BuildEnvironment
from sphinx.events import EventManager
from sphinx.project import Project
from sphinx.registry import SphinxComponentRegistry
from sphinx.util.docutils import additional_nodes, sphinx_domains, unregister_node
from sphinx.util.tags import Tags

from myst_parser.docutils_renderer import DocutilsRenderer


class SphinxRenderer(DocutilsRenderer):
    """A mistletoe renderer to populate (in-place) a `docutils.document` AST.

    This is sub-class of `DocutilsRenderer` that handles sphinx cross-referencing.
    """

    def handle_cross_reference(self, token, destination):
        """Create nodes for references that are not immediately resolvable."""
        wrap_node = addnodes.pending_xref(
            reftarget=unquote(destination),
            reftype="any",
            refdomain=None,  # Added to enable cross-linking
            refexplicit=len(token.children) > 0,
            refwarn=True,
        )
        self.add_line_and_source_path(wrap_node, token)
        title = token.attrGet("title")
        if title:
            wrap_node["title"] = title
        self.current_node.append(wrap_node)
        text_node = nodes.literal("", "", classes=["xref", "any"])
        wrap_node.append(text_node)
        with self.current_node_context(text_node):
            self.render_children(token)

    def render_math_block_eqno(self, token):
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

    def add_math_target(self, node):
        # Code mainly copied from sphinx.directives.patches.MathDirective
        env = self.document.settings.env

        # register label to domain
        domain = cast(MathDomain, env.get_domain("math"))
        domain.note_equation(env.docname, node["label"], location=node)
        node["number"] = domain.get_equation_number_for(node["label"])
        node["docname"] = env.docname

        # create target node
        node_id = nodes.make_id("equation-%s" % node["label"])
        target = nodes.target("", "", ids=[node_id])
        self.document.note_explicit_target(target)
        return target


def minimal_sphinx_app(configuration=None, sourcedir=None):
    """Create a minimal Sphinx environment; loading sphinx roles, directives, etc.
    """

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

            with tempfile.TemporaryDirectory() as tempdir:
                # creating a builder attempts to make the doctreedir
                self.doctreedir = tempdir
                self.builder = self.create_builder(buildername)
            self.doctreedir = None

    app = MockSphinx(confoverrides=configuration, srcdir=sourcedir)
    return app


@contextmanager
def mock_sphinx_env(conf=None, srcdir=None, document=None):
    """Set up an environment, to parse sphinx roles/directives,
    outside of a `sphinx-build`.

    :param conf: a dictionary representation of the sphinx `conf.py`
    :param srcdir: a path to a source directory
        (for example, can be used for `include` statements)

    This primarily copies the code in `sphinx.util.docutils.docutils_namespace`
    and `sphinx.util.docutils.sphinx_domains`.
    """
    # store currently loaded roles/directives, so we can revert on exit
    _directives = copy.copy(directives._directives)
    _roles = copy.copy(roles._roles)
    # Monkey-patch directive and role dispatch,
    # so that sphinx domain-specific markup takes precedence.
    app = minimal_sphinx_app(configuration=conf, sourcedir=srcdir)
    _sphinx_domains = sphinx_domains(app.env)
    _sphinx_domains.enable()
    if document is not None:
        document.settings.env = app.env
    try:
        yield app
    finally:
        # revert loaded roles/directives
        directives._directives = _directives
        roles._roles = _roles
        # TODO unregister nodes (see `sphinx.util.docutils.docutils_namespace`)
        for node in list(additional_nodes):
            unregister_node(node)
            additional_nodes.discard(node)
        # revert directive/role function (see `sphinx.util.docutils.sphinx_domains`)
        _sphinx_domains.disable()
