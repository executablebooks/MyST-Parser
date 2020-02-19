import html
from itertools import chain
import re

from mistletoe import block_token, span_token
from mistletoe import html_renderer

from myst_parser import span_tokens as myst_span_tokens
from myst_parser import block_tokens as myst_block_tokens


class HTMLRenderer(html_renderer.HTMLRenderer):
    def __init__(self, add_mathjax=False):
        """This HTML render uses the same block/span tokens as the docutils renderer.

        It is used to test compliance with the commonmark spec.
        """
        self._suppress_ptag_stack = [False]

        _span_tokens = self._tokens_from_module(myst_span_tokens)
        _block_tokens = self._tokens_from_module(myst_block_tokens)

        super(html_renderer.HTMLRenderer, self).__init__(
            *chain(_block_tokens, _span_tokens)
        )

        span_token._token_types.value = _span_tokens
        block_token._token_types.value = _block_tokens

        # html.entities.html5 includes entitydefs not ending with ';',
        # CommonMark seems to hate them, so...
        self._stdlib_charref = html._charref
        _charref = re.compile(
            r"&(#[0-9]+;" r"|#[xX][0-9a-fA-F]+;" r"|[^\t\n\f <&#;]{1,32};)"
        )
        html._charref = _charref

        self.mathjax_src = ""
        if add_mathjax:
            self.mathjax_src = (
                "<script src="
                '"https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.0/MathJax.js'
                '?config=TeX-MML-AM_CHTML"></script>\n'
            )

    def render_code_fence(self, token):
        return self.render_block_code(token)

    def render_front_matter(self, token):
        raise NotImplementedError

    def render_line_comment(self, token):
        raise NotImplementedError

    def render_target(self, token):
        raise NotImplementedError

    def render_math(self, token):
        """
        Ensure Math tokens are all enclosed in two dollar signs.
        """
        if token.content.startswith("$$"):
            return self.render_raw_text(token)
        return "${}$".format(self.render_raw_text(token))

    def render_document(self, token):
        """
        Optionally Append CDN link for MathJax to the end of <body>.
        """
        return super().render_document(token) + self.mathjax_src
