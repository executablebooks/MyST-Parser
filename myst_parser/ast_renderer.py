"""Abstract syntax tree renderer for myst."""
from itertools import chain
import json

from mistletoe import block_token, span_token
from mistletoe import ast_renderer

from myst_parser import span_tokens as myst_span_tokens
from myst_parser import block_tokens as myst_block_tokens


class AstRenderer(ast_renderer.ASTRenderer):
    def __init__(self):
        """This AST render uses the same block/span tokens as the docutils renderer."""

        _span_tokens = self._tokens_from_module(myst_span_tokens)
        _block_tokens = self._tokens_from_module(myst_block_tokens)

        super(ast_renderer.ASTRenderer, self).__init__(
            *chain(_block_tokens, _span_tokens)
        )

        span_token._token_types.value = _span_tokens
        block_token._token_types.value = _block_tokens

    def render(self, token, to_json=False):
        """
        Returns the string representation of the AST.

        Overrides super().render. Delegates the logic to get_ast.
        """
        ast = ast_renderer.get_ast(token)
        if to_json:
            return json.dumps(ast, indent=2) + "\n"
        return ast
