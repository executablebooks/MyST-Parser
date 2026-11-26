"""A module for compatibility with the docutils>=0.17 `include` directive, in RST documents.

For example::

   .. include::  path/to/file.md
      :parser: myst_parser.sphinx_
"""

from docutils import nodes

from myst_parser.parsers.sphinx_ import MystParser


class Parser(MystParser):
    """MyST parser for an rST ``include`` directive using Sphinx."""

    def parse(self, inputstring: str, document: nodes.document) -> None:
        document._myst_included_by_rst = True
        super().parse(inputstring, document)
