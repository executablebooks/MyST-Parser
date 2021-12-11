"""A module for compatibility with the docutils>=0.17 `include` directive, in RST documents::

   .. include::  path/to/file.md
      :parser: myst_parser.sphinx_
"""
from myst_parser.sphinx_parser import MystParser as Parser  # noqa: F401
