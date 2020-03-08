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
    :special-members: __init__, __enter__, __exit__
    :members: default_block_tokens, default_span_tokens
    :undoc-members:
    :member-order: alphabetical
    :show-inheritance:


JSON
....

.. autoclass:: myst_parser.json_renderer.JsonRenderer
    :special-members: __init__, __enter__, __exit__
    :members: default_block_tokens, default_span_tokens
    :undoc-members:
    :member-order: alphabetical
    :show-inheritance:

Docutils
........

.. autoclass:: myst_parser.docutils_renderer.DocutilsRenderer
    :special-members: __init__, __enter__, __exit__
    :members: default_block_tokens, default_span_tokens, new_document
    :undoc-members:
    :member-order: alphabetical
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
    :special-members: __init__, __enter__, __exit__
    :members: default_block_tokens, default_span_tokens, mock_sphinx_env
    :undoc-members:
    :member-order: alphabetical
    :show-inheritance:

.. autofunction:: myst_parser.docutils_renderer.dict_to_docinfo
