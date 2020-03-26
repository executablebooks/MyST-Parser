from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML
from markdown_it.extensions.front_matter import front_matter_plugin
from markdown_it.extensions.myst_blocks import myst_block_plugin
from markdown_it.extensions.myst_role import myst_role_plugin
from markdown_it.extensions.texmath import texmath_plugin
from markdown_it.extensions.footnote import footnote_plugin

from myst_parser.docutils_renderer import DocutilsRenderer
from myst_parser.docutils_renderer import make_document


def default_parser(renderer="sphinx") -> MarkdownIt:
    from myst_parser.sphinx_renderer import SphinxRenderer

    renderers = {
        "sphinx": SphinxRenderer,
        "docutils": DocutilsRenderer,
        "html": RendererHTML,
    }
    renderer_cls = renderers[renderer]

    md = (
        MarkdownIt("commonmark", renderer_cls=renderer_cls)
        .enable("table")
        .use(front_matter_plugin)
        .use(myst_block_plugin)
        .use(myst_role_plugin)
        .use(texmath_plugin)
        .use(footnote_plugin)
        .disable("footnote_inline")
        # disable this for now, because it need a new implementation in the renderer
        .disable("footnote_tail")
        # we don't want to yet remove un-referenced, because they may be referenced
        # in admonition type directives
        # we need to do our own post process to gather them
        # (and also add nodes.transition() above)
    )
    return md


def to_docutils(text, options=None, env=None, document=None, in_sphinx_env=False):
    md = default_parser()
    if options:
        md.options.update(options)
    md.options["document"] = document or make_document()
    if in_sphinx_env:
        from myst_parser.sphinx_renderer import mock_sphinx_env

        with mock_sphinx_env(document=md.options["document"]):
            return md.render(text, env)
    else:
        return md.render(text, env)


def to_html(text, env=None):
    md = default_parser("html")
    return md.render(text, env)


def to_tokens(text, env=None):
    md = default_parser()
    return md.parse(text, env)
