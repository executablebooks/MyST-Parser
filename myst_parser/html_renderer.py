from typing import Optional

from mistletoe import block_tokens, block_tokens_ext, span_tokens, span_tokens_ext
from mistletoe.parse_context import ParseContext
from mistletoe.renderers import html as html_renderer

from myst_parser.block_tokens import LineComment, BlockBreak, Quote, Paragraph, List
from myst_parser.span_tokens import Role, Target


class HTMLRenderer(html_renderer.HTMLRenderer):
    """This HTML render uses the uses the MyST spec block and span tokens.

    It is used to test compliance with the commonmark spec,
    and can be used for basic previews,
    but does not run roles/directives, resolve cross-references etc...
    """

    default_block_tokens = (
        block_tokens.HTMLBlock,
        LineComment,
        block_tokens.BlockCode,
        block_tokens.Heading,
        Quote,
        block_tokens.CodeFence,
        block_tokens.ThematicBreak,
        BlockBreak,
        List,
        block_tokens_ext.Table,
        block_tokens_ext.Footnote,
        block_tokens.LinkDefinition,
        Paragraph,
    )

    default_span_tokens = (
        span_tokens.EscapeSequence,
        Role,
        span_tokens.HTMLSpan,
        span_tokens.AutoLink,
        Target,
        span_tokens.CoreTokens,
        span_tokens_ext.FootReference,
        span_tokens_ext.Math,
        # TODO there is no matching core element in docutils for strikethrough
        # span_tokens_ext.Strikethrough,
        span_tokens.InlineCode,
        span_tokens.LineBreak,
        span_tokens.RawText,
    )

    def __init__(
        self,
        parse_context: Optional[ParseContext] = None,
        add_mathjax=False,
        as_standalone=False,
        add_css=None,
    ):
        """Intitalise HTML renderer

        :param parse_context: the parse context stores global parsing variables,
            such as the block/span tokens to search for,
            and link/footnote definitions that have been collected.
            If None, a new context will be instatiated, with the default
            block/span tokens for this renderer.
            These will be re-instatiated on ``__enter__``.
        :type parse_context: mistletoe.parse_context.ParseContext
        :param add_mathjax: add the mathjax CDN
        :param as_standalone: return the HTML body within a minmal HTML page
        :param add_css: if as_standalone=True, CSS to add to the header
        """
        super().__init__(parse_context=parse_context, as_standalone=False)

        self.mathjax_src = ""
        if add_mathjax:
            self.mathjax_src = (
                "<script src="
                '"https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.0/MathJax.js'
                '?config=TeX-MML-AM_CHTML"></script>\n'
            )
        self._as_standalone = as_standalone
        self._add_css = add_css

    def render_document(self, token):
        """
        Optionally Append CDN link for MathJax to the end of <body>.
        """
        front_matter = ""
        if token.front_matter:
            front_matter = (
                '<div class="myst-front-matter">'
                '<pre><code class="language-yaml">{}</code></pre>'
                "</div>\n"
            ).format(self.escape_html(token.front_matter.content))
        body = front_matter + super().render_document(token) + self.mathjax_src
        if not self._as_standalone:
            return body
        return html_renderer.minimal_html_page(body, css=self._add_css or "")

    def render_code_fence(self, token):
        if token.language and token.language.startswith("{"):
            return self.render_directive(token)
        return self.render_block_code(token)

    def render_directive(self, token):
        return (
            '<div class="myst-directive">\n'
            "<pre><code>{name} {args}\n{content}</code></pre></span>\n"
            "</div>"
        ).format(
            name=self.escape_html(token.language),
            args=self.escape_html(token.arguments),
            content=self.escape_html(token.children[0].content),
        )

    def render_line_comment(self, token):
        return "<!-- {} -->".format(self.escape_html(token.content))

    def render_block_break(self, token):
        return '<!-- myst-block-data {} -->\n<hr class="myst-block-break" />'.format(
            self.escape_html(token.content)
        )

    def render_target(self, token):
        return (
            '<a class="myst-target" href="#{0}" title="Permalink to here">({0})=</a>'
        ).format(self.escape_html(token.target))

    def render_role(self, token):
        return ('<span class="myst-role"><code>{{{0}}}{1}</code></span>').format(
            self.escape_html(token.role_name), self.render_raw_text(token.children[0])
        )

    def render_math(self, token):
        """
        Ensure Math tokens are all enclosed in two dollar signs.
        """
        if token.content.startswith("$$"):
            return self.render_raw_text(token)
        return "${}$".format(self.render_raw_text(token))
