.. _api/renderers:

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
    :members: handle_cross_reference, render_math_block_eqno
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

.. autofunction:: myst_parser.docutils_renderer.dict_to_field_list

.. autofunction:: myst_parser.sphinx_renderer.minimal_sphinx_app

.. autofunction:: myst_parser.sphinx_renderer.mock_sphinx_env
