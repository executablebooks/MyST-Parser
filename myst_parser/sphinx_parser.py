import time
from os import path
from typing import Tuple

from docutils import nodes
from docutils.core import publish_doctree
from docutils.parsers.rst import Parser as RstParser
from markdown_it.token import Token
from markdown_it.utils import AttrDict
from sphinx.application import Sphinx
from sphinx.io import SphinxStandaloneReader
from sphinx.parsers import Parser
from sphinx.util import logging
from sphinx.util.docutils import sphinx_domains

from myst_parser.main import MdParserConfig, default_parser

SPHINX_LOGGER = logging.getLogger(__name__)


class MystParser(Parser):
    """Docutils parser for Markedly Structured Text (MyST)."""

    supported: Tuple[str, ...] = ("md", "markdown", "myst")
    """Aliases this parser supports."""

    settings_spec = RstParser.settings_spec
    """Runtime settings specification.

    Defines runtime settings and associated command-line options, as used by
    `docutils.frontend.OptionParser`.  This is a concatenation of tuples of:

    - Option group title (string or `None` which implies no group, just a list
      of single options).

    - Description (string or `None`).

    - A sequence of option tuples
    """

    config_section = "myst parser"
    config_section_dependencies = ("parsers",)
    translate_section_name = None

    def parse(
        self, inputstring: str, document: nodes.document, renderer: str = "sphinx"
    ) -> None:
        """Parse source text.

        :param inputstring: The source string to parse
        :param document: The root docutils node to add AST elements to

        """
        if renderer == "sphinx":
            config = document.settings.env.myst_config
        else:
            config = MdParserConfig()
        parser = default_parser(config)
        parser.options["document"] = document
        env = AttrDict()
        tokens = parser.parse(inputstring, env)
        if not tokens or tokens[0].type != "front_matter":
            # we always add front matter, so that we can merge it with global keys,
            # specified in the sphinx configuration
            tokens = [Token("front_matter", "", 0, content="{}", map=[0, 0])] + tokens
        parser.renderer.render(tokens, parser.options, env)


def parse(app: Sphinx, text: str, docname: str = "index") -> nodes.document:
    """Parse a string as MystMarkdown with Sphinx application."""
    app.env.temp_data["docname"] = docname
    app.env.all_docs[docname] = time.time()
    reader = SphinxStandaloneReader()
    reader.setup(app)
    parser = MystParser()
    parser.set_application(app)
    with sphinx_domains(app.env):
        return publish_doctree(
            text,
            path.join(app.srcdir, docname + ".md"),
            reader=reader,
            parser=parser,
            parser_name="markdown",
            settings_overrides={"env": app.env, "gettext_compact": True},
        )
