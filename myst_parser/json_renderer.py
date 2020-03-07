"""JSON renderer for myst."""
from itertools import chain

from mistletoe.parse_context import ParseContext, set_parse_context, tokens_from_module
from mistletoe.renderers import json

from myst_parser import span_tokens
from myst_parser import block_tokens


class JsonRenderer(json.JsonRenderer):
    def __init__(self):
        """This AST render uses the same block/span tokens as the docutils renderer."""
        super().__init__()
        myst_span_tokens = tokens_from_module(span_tokens)
        myst_block_tokens = tokens_from_module(block_tokens)

        for token in chain(myst_span_tokens, myst_block_tokens):
            render_func = getattr(self, self._cls_to_func(token.__name__))
            self.render_map[token.__name__] = render_func

        parse_context = ParseContext(myst_block_tokens, myst_span_tokens)
        set_parse_context(parse_context)
        self.parse_context = parse_context.copy()
