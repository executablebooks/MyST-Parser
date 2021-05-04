import copy
import tempfile
from contextlib import contextmanager
from io import StringIO
from typing import Optional, cast
from urllib.parse import unquote
from uuid import uuid4

from docutils import nodes
from docutils.parsers.rst import directives, roles
from markdown_it.tree import SyntaxTreeNode
from sphinx import addnodes
from sphinx.application import Sphinx, builtin_extensions
from sphinx.config import Config
from sphinx.domains.math import MathDomain
from sphinx.domains.std import StandardDomain
from sphinx.environment import BuildEnvironment
from sphinx.events import EventManager
from sphinx.project import Project
from sphinx.registry import SphinxComponentRegistry
from sphinx.util import logging
from sphinx.util.docutils import additional_nodes, sphinx_domains, unregister_node
from sphinx.util.nodes import clean_astext
from sphinx.util.tags import Tags

from myst_parser.docutils_renderer import DocutilsRenderer

LOGGER = logging.getLogger(__name__)


class SphinxRenderer(DocutilsRenderer):
    """A markdown-it-py renderer to populate (in-place) a `docutils.document` AST.

    This is sub-class of `DocutilsRenderer` that handles sphinx specific aspects,
    such as cross-referencing.
    """

    @property
    def doc_env(self) -> BuildEnvironment:
        return self.document.settings.env

    def create_warning(
        self,
        message: str,
        *,
        line: Optional[int] = None,
        append_to: Optional[nodes.Element] = None,
        wtype: str = "myst",
        subtype: str = "other",
    ) -> Optional[nodes.system_message]:
        """Generate a warning, logging it if necessary.

        If the warning type is listed in the ``suppress_warnings`` configuration,
        then ``None`` will be returned and no warning logged.
        """
        message = f"{message} [{wtype}.{subtype}]"
        kwargs = {"line": line} if line is not None else {}

        if not logging.is_suppressed_warning(
            wtype, subtype, self.doc_env.app.config.suppress_warnings
        ):
            msg_node = self.reporter.warning(message, **kwargs)
            if append_to is not None:
                append_to.append(msg_node)
        return None

    def handle_cross_reference(self, token: SyntaxTreeNode, destination: str) -> None:
        """Create nodes for references that are not immediately resolvable."""
        wrap_node = addnodes.pending_xref(
            refdoc=self.doc_env.docname,
            reftarget=unquote(destination),
            reftype="myst",
            refdomain=None,  # Added to enable cross-linking
            refexplicit=len(token.children or []) > 0,
            refwarn=True,
        )
        self.add_line_and_source_path(wrap_node, token)
        title = token.attrGet("title")
        if title:
            wrap_node["title"] = title
        self.current_node.append(wrap_node)

        inner_node = nodes.inline("", "", classes=["xref", "myst"])
        wrap_node.append(inner_node)
        with self.current_node_context(inner_node):
            self.render_children(token)

    def render_heading(self, token: SyntaxTreeNode) -> None:
        """This extends the docutils method, to allow for the addition of heading ids.
        These ids are computed by the ``markdown-it-py`` ``anchors_plugin``
        as "slugs" which are unique document.

        The approach is similar to ``sphinx.ext.autosectionlabel``
        """
        super().render_heading(token)
        slug = cast(str, token.attrGet("id"))
        if slug is None:
            return

        section = self.current_node
        doc_slug = self.doc_env.doc2path(self.doc_env.docname, base=False) + "#" + slug

        # save the reference in the standard domain, so that it can be handled properly
        domain = cast(StandardDomain, self.doc_env.get_domain("std"))
        if doc_slug in domain.labels:
            other_doc = self.doc_env.doc2path(domain.labels[doc_slug][0])
            self.create_warning(
                f"duplicate label {doc_slug}, other instance in {other_doc}",
                line=section.line,
                subtype="anchor",
            )
        labelid = section["ids"][0]
        domain.anonlabels[doc_slug] = self.doc_env.docname, labelid
        domain.labels[doc_slug] = (
            self.doc_env.docname,
            labelid,
            clean_astext(section[0]),
        )

        # for debugging
        if not hasattr(self.doc_env, "myst_anchors"):
            self.doc_env.myst_anchors = True  # type: ignore[attr-defined]
        section["myst-anchor"] = doc_slug

    def render_math_block_eqno(self, token: SyntaxTreeNode) -> None:
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
        domain = cast(MathDomain, self.doc_env.get_domain("math"))
        domain.note_equation(self.doc_env.docname, node["label"], location=node)
        node["number"] = domain.get_equation_number_for(node["label"])
        node["docname"] = self.doc_env.docname

        # create target node
        node_id = nodes.make_id("equation-%s" % node["label"])
        target = nodes.target("", "", ids=[node_id])
        self.document.note_explicit_target(target)
        return target


def minimal_sphinx_app(
    configuration=None, sourcedir=None, with_builder=False, raise_on_warning=False
):
    """Create a minimal Sphinx environment; loading sphinx roles, directives, etc."""

    class MockSphinx(Sphinx):
        """Minimal sphinx init to load roles and directives."""

        def __init__(self, confoverrides=None, srcdir=None, raise_on_warning=False):
            self.extensions = {}
            self.registry = SphinxComponentRegistry()
            self.html_themes = {}
            self.events = EventManager(self)

            # logging
            self.verbosity = 0
            self._warncount = 0
            self.warningiserror = raise_on_warning
            self._status = StringIO()
            self._warning = StringIO()
            logging.setup(self, self._status, self._warning)

            self.tags = Tags([])
            self.config = Config({}, confoverrides or {})
            self.config.pre_init_values()
            self._init_i18n()
            for extension in builtin_extensions:
                self.registry.load_extension(self, extension)
            # fresh env
            self.doctreedir = ""
            self.srcdir = srcdir
            self.confdir = None
            self.outdir = ""
            self.project = Project(srcdir=srcdir, source_suffix={".md": "markdown"})
            self.project.docnames = {"mock_docname"}
            self.env = BuildEnvironment()
            self.env.setup(self)
            self.env.temp_data["docname"] = "mock_docname"
            # Ignore type checkers because we disrespect superclass typing here
            self.builder = None  # type: ignore[assignment]

            if not with_builder:
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
            self.doctreedir = ""

    app = MockSphinx(
        confoverrides=configuration, srcdir=sourcedir, raise_on_warning=raise_on_warning
    )
    return app


@contextmanager
def mock_sphinx_env(
    conf=None, srcdir=None, document=None, with_builder=False, raise_on_warning=False
):
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
    app = minimal_sphinx_app(
        configuration=conf,
        sourcedir=srcdir,
        with_builder=with_builder,
        raise_on_warning=raise_on_warning,
    )
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
