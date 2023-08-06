"""MyST Markdown parser for sphinx."""
from __future__ import annotations

from docutils import nodes
from docutils.parsers.rst import Parser as RstParser
from sphinx.parsers import Parser as SphinxParser
from sphinx.util import logging

from myst_parser.config.main import (
    MdParserConfig,
    TopmatterReadError,
    merge_file_level,
    read_topmatter,
)
from myst_parser.mdit_to_docutils.sphinx_ import SphinxRenderer
from myst_parser.mdit_to_docutils.transforms import ResolveAnchorIds
from myst_parser.parsers.mdit import create_md_parser
from myst_parser.warnings_ import create_warning

SPHINX_LOGGER = logging.getLogger(__name__)


class MystParser(SphinxParser):
    """Sphinx parser for Markedly Structured Text (MyST)."""

    supported: tuple[str, ...] = ("md", "markdown", "myst")
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

    def get_transforms(self):
        return super().get_transforms() + [ResolveAnchorIds]

    def parse(self, inputstring: str, document: nodes.document) -> None:
        """Parse source text.

        :param inputstring: The source string to parse
        :param document: The root docutils node to add AST elements to

        """
        # get the global config
        config: MdParserConfig = document.settings.env.myst_config

        # update the global config with the file-level config
        try:
            topmatter = read_topmatter(inputstring)
        except TopmatterReadError:
            pass  # this will be reported during the render
        else:
            if topmatter:
                warning = lambda wtype, msg: create_warning(  # noqa: E731
                    document, msg, wtype, line=1, append_to=document
                )
                config = merge_file_level(config, topmatter, warning)

        # inject label references for a partial document string
        #
        # When processing translations in Sphinx, after Sphinx's i8n transform
        # replaces parts of a document with a translation, document is
        # processed a message at a time through the MyST-parser. For
        # references using link labels, these may not be to the parse for the
        # specific messages that need them. If we detect we have a cache of
        # label references (from an initial pass before translation), rebuild
        # the label references and append them to the specific message about
        # to be parsed. This will ensure references will be resolved/built as
        # expected.
        env = document.settings.env
        labelrefs = env.metadata[env.docname].get('myst_labelrefs', {})
        if labelrefs:
            postfix = '\n\n'
            for label, uri in labelrefs.items():
                postfix += f'[{label}]: {uri}\n'
            inputstring += postfix

        parser = create_md_parser(config, SphinxRenderer)
        parser.options["document"] = document
        parser.render(inputstring)
