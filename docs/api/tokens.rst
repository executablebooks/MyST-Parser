.. _api/tokens:

Extended AST Tokens
-------------------

MyST builds on the mistletoe
:ref:`core block tokens <mistletoe:tokens/block>` and
:ref:`core span tokens <mistletoe:tokens/span>`
to extend the syntax (as discussed in :ref:`example_syntax`).

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


Math
....

.. autoclass:: myst_parser.span_tokens.Math
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
