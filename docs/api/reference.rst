=============
API Reference
=============

.. _api/directive:

Directive Parsing Reference
---------------------------

.. automodule:: myst_parser.parse_directives
    :members:

MyST Renderers
--------------


These renderers take the markdown-it parsed token stream and convert it to
the docutils AST. The sphinx renderer is a subclass of the docutils one,
with some additional methods only available *via* sphinx
.e.g. multi-document cross-referencing.


Docutils
........

.. autoclass:: myst_parser.docutils_renderer.DocutilsRenderer
    :special-members: __output__, __init__
    :members: render, nested_render_text, add_line_and_source_path, current_node_context
    :undoc-members:
    :member-order: bysource
    :show-inheritance:


Sphinx
......

.. autoclass:: myst_parser.sphinx_renderer.SphinxRenderer
    :special-members: __output__
    :members: handle_cross_reference, render_math_block_label
    :undoc-members:
    :member-order: alphabetical
    :show-inheritance:

Mocking
.......

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


Additional Methods
..................

.. autofunction:: myst_parser.docutils_renderer.make_document

.. autofunction:: myst_parser.docutils_renderer.html_meta_to_nodes

.. autofunction:: myst_parser.sphinx_renderer.minimal_sphinx_app

.. autofunction:: myst_parser.sphinx_renderer.mock_sphinx_env



.. _api/sphinx_parser:

Sphinx Parser Reference
-----------------------

This class builds on the :py:class:`~myst_parser.sphinx_renderer.SphinxRenderer`
to generate a parser for Sphinx, using the :ref:`Sphinx parser API <sphinx:parser-api>`:

.. autoclass:: myst_parser.sphinx_parser.MystParser
    :members: supported, parse
    :undoc-members:
    :member-order: bysource
    :show-inheritance:
    :exclude-members: __init__

.. _api/renderers:
