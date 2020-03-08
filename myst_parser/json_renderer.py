"""JSON renderer for myst."""
from mistletoe import block_tokens, block_tokens_ext, span_tokens, span_tokens_ext
from mistletoe.renderers import json

from myst_parser.block_tokens import LineComment, BlockBreak, Quote, Paragraph, List
from myst_parser.span_tokens import Role, Target


class JsonRenderer(json.JsonRenderer):
    """This JSON render uses the MyST spec block and span tokens.
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
        span_tokens_ext.Math,
        # TODO there is no matching core element in docutils for strikethrough
        # span_tokens_ext.Strikethrough,
        span_tokens.InlineCode,
        span_tokens.LineBreak,
        span_tokens.RawText,
    )
