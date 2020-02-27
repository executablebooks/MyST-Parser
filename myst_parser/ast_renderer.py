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


def get_ast(token):
    """
    Recursively unrolls token attributes into dictionaries (token.children
    into lists).

    Returns:
        a dictionary of token's attributes.
    """
    node = {}
    # Python 3.6 uses [ordered dicts] [1].
    # Put in 'type' entry first to make the final tree format somewhat
    # similar to [MDAST] [2].
    #
    #   [1]: https://docs.python.org/3/whatsnew/3.6.html
    #   [2]: https://github.com/syntax-tree/mdast
    node["type"] = token.__class__.__name__
    # here we ignore 'private' underscore attribute
    node.update({k: v for k, v in token.__dict__.items() if not k.startswith("_")})
    if "header" in node:
        node["header"] = get_ast(node["header"])
    if "children" in node:
        node["children"] = [get_ast(child) for child in node["children"]]
    return node
