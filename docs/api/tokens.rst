.. _api/tokens:

Extended AST Tokens
-------------------

MyST builds on the mistletoe tokens, to extend the syntax:

- :ref:`Core block tokens <mistletoe:tokens/block>`
- :ref:`Core span tokens <mistletoe:tokens/span>`
- :ref:`Extension tokens <mistletoe:tokens/extension>`


.. seealso::

    :ref:`example_syntax`


LineComment
...........

.. autoclass:: myst_parser.block_tokens.LineComment
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__


BlockBreak
..........

.. autoclass:: myst_parser.block_tokens.BlockBreak
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__


Role
....

.. autoclass:: myst_parser.span_tokens.Role
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__


Target
......

.. autoclass:: myst_parser.span_tokens.Target
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__
