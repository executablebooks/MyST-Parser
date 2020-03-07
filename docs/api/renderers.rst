.. _api/renderers:

MyST Renderers
--------------

MyST-Parser builds on the mistletoe
:ref:`core renderers <mistletoe:renderers/core>`
by including the extended tokens, listed in :ref:`api/tokens`,
and adding bridges to docutils/sphinx:

HTML
....

.. autoclass:: myst_parser.html_renderer.HTMLRenderer
    :members:
    :undoc-members:
    :show-inheritance:


JSON
....

.. autoclass:: myst_parser.json_renderer.JsonRenderer
    :members:
    :undoc-members:
    :show-inheritance:

Docutils
........

.. autoclass:: myst_parser.docutils_renderer.DocutilsRenderer
    :members:
    :undoc-members:
    :show-inheritance:


.. autoclass:: myst_parser.docutils_renderer.MockInliner
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: myst_parser.docutils_renderer.MockState
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: myst_parser.docutils_renderer.MockStateMachine
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: myst_parser.docutils_renderer.MockIncludeDirective
    :members:
    :undoc-members:
    :show-inheritance:

Sphinx
......

.. autoclass:: myst_parser.docutils_renderer.SphinxRenderer
    :members:
    :undoc-members:
    :show-inheritance:
