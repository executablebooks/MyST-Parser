.. _api/main:

==========
Python API
==========

Source text parsers
-------------------

.. _api/docutils_parser:

Docutils
........

.. autoclass:: myst_parser.docutils_.Parser
    :members: parse
    :undoc-members:
    :member-order: bysource
    :show-inheritance:

.. _api/sphinx_parser:

Sphinx
......

.. autoclass:: myst_parser.parsers.sphinx_.MystParser
    :members: supported, parse
    :undoc-members:
    :member-order: bysource
    :show-inheritance:
    :exclude-members: __init__

.. _api/renderers:

Markdown-it to docutils
-----------------------

These renderers take the markdown-it parsed token stream and convert it to
the docutils AST. The sphinx renderer is a subclass of the docutils one,
with some additional methods only available *via* sphinx e.g. multi-document cross-referencing.


Docutils
........

.. autoclass:: myst_parser.mdit_to_docutils.base.DocutilsRenderer
    :special-members: __output__, __init__
    :members: render, nested_render_text, add_line_and_source_path, current_node_context
    :undoc-members:
    :member-order: bysource
    :show-inheritance:


Sphinx
......

.. autoclass:: myst_parser.mdit_to_docutils.sphinx_.SphinxRenderer
    :special-members: __output__
    :members: render_internal_link, render_math_block_label
    :undoc-members:
    :member-order: alphabetical
    :show-inheritance:

.. _api/directive:

Directive and role processing
-----------------------------

This module processes the content of a directive:

.. automodule:: myst_parser.parsers.directives
    :members:

These classes are parsed to sphinx roles and directives,
to mimic the original docutls rST specific parser elements,
but instead run nested parsing with the markdown parser.

.. autoclass:: myst_parser.mocking.MockInliner
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: myst_parser.mocking.MockState
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: myst_parser.mocking.MockStateMachine
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: myst_parser.mocking.MockIncludeDirective
    :members:
    :undoc-members:
    :show-inheritance:
