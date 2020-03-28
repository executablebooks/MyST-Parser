from typing import List

from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML
from markdown_it.extensions.front_matter import front_matter_plugin
from markdown_it.extensions.myst_blocks import myst_block_plugin
from markdown_it.extensions.myst_role import myst_role_plugin
from markdown_it.extensions.texmath import texmath_plugin
from markdown_it.extensions.footnote import footnote_plugin

from . import __version__  # noqa: F401


def default_parser(
    renderer="sphinx", disable_syntax=(), math_delimiters="dollars"
) -> MarkdownIt:
    """Return the default parser configuration for MyST"""
    if renderer == "sphinx":
        from myst_parser.sphinx_renderer import SphinxRenderer

        renderer_cls = SphinxRenderer
    elif renderer == "html":
        renderer_cls = RendererHTML
    elif renderer == "docutils":
        from myst_parser.docutils_renderer import DocutilsRenderer

        renderer_cls = DocutilsRenderer
    else:
        raise ValueError("unknown renderer type: {0}".format(renderer))

    md = (
        MarkdownIt("commonmark", renderer_cls=renderer_cls)
        .enable("table")
        .use(front_matter_plugin)
        .use(myst_block_plugin)
        .use(myst_role_plugin)
        .use(texmath_plugin, delimiters=math_delimiters)
        .use(footnote_plugin)
        .disable("footnote_inline")
        # disable this for now, because it need a new implementation in the renderer
        .disable("footnote_tail")
        # we don't want to yet remove un-referenced, because they may be referenced
        # in admonition type directives
        # so we do our own post processing
    )
    for name in disable_syntax:
        md.disable(name, True)
    return md


def to_docutils(
    text: str,
    options=None,
    env=None,
    disable_syntax: List[str] = (),
    math_delimiters: str = "dollars",
    renderer="sphinx",
    document=None,
    in_sphinx_env: bool = False,
    conf=None,
    srcdir=None,
):
    """Render text to the docutils AST

    :param text: the text to render
    :param options: options to update the parser with
    :param env: The sandbox environment for the parse
        (will contain e.g. reference definitions)
    :param disable_syntax: list of syntax element names to disable
    :param document: the docutils root node to use (otherwise a new one will be created)
    :param in_sphinx_env: initialise a minimal sphinx environment (useful for testing)
    :param conf: the sphinx conf.py as a dictionary
    :param srcdir: to parse to the mock sphinc env

    :returns: docutils document
    """
    from myst_parser.docutils_renderer import make_document

    md = default_parser(
        renderer=renderer,
        disable_syntax=disable_syntax,
        math_delimiters=math_delimiters,
    )
    if options:
        md.options.update(options)
    md.options["document"] = document or make_document()
    if in_sphinx_env:
        from myst_parser.sphinx_renderer import mock_sphinx_env

        with mock_sphinx_env(conf=conf, srcdir=srcdir, document=md.options["document"]):
            return md.render(text, env)
    else:
        return md.render(text, env)


def to_html(text: str, env=None):
    md = default_parser("html")
    return md.render(text, env)


def to_tokens(text: str, env=None):
    md = default_parser("html")
    return md.parse(text, env)
