"""A module for compatibility with the docutils>=0.17 `include` directive, in RST documents::

   .. include::
      :parser: myst_parser.docutils_
"""
from typing import Tuple

from docutils import nodes
from docutils.parsers.rst import Parser as RstParser
from markdown_it.token import Token
from markdown_it.utils import AttrDict

from myst_parser.main import MdParserConfig, default_parser


class Parser(RstParser):
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

    def parse(self, inputstring: str, document: nodes.document) -> None:
        """Parse source text.

        :param inputstring: The source string to parse
        :param document: The root docutils node to add AST elements to

        """
        config = MdParserConfig(renderer="docutils")
        parser = default_parser(config)
        parser.options["document"] = document
        env = AttrDict()
        tokens = parser.parse(inputstring, env)
        if not tokens or tokens[0].type != "front_matter":
            # we always add front matter, so that we can merge it with global keys,
            # specified in the sphinx configuration
            tokens = [Token("front_matter", "", 0, content="{}", map=[0, 0])] + tokens
        parser.renderer.render(tokens, parser.options, env)
