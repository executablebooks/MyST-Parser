from typing import List, Optional

import attr
from attr.validators import deep_iterable, in_, instance_of, optional

from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML
from markdown_it.extensions.front_matter import front_matter_plugin
from markdown_it.extensions.myst_blocks import myst_block_plugin
from markdown_it.extensions.myst_role import myst_role_plugin

# from markdown_it.extensions.texmath import texmath_plugin
from markdown_it.extensions.dollarmath import dollarmath_plugin
from markdown_it.extensions.footnote import footnote_plugin
from markdown_it.extensions.amsmath import amsmath_plugin
from markdown_it.extensions.container import container_plugin
from markdown_it.extensions.deflist import deflist_plugin
from markdown_it.extensions.anchors import anchors_plugin

from . import __version__  # noqa: F401


@attr.s()
class MdParserConfig:
    """Configuration options for the Markdown Parser.

    Note in the sphinx configuration these option names are prepended with ``myst_``
    """

    renderer: str = attr.ib(
        default="sphinx", validator=in_(["sphinx", "html", "docutils"])
    )
    commonmark_only: bool = attr.ib(default=False, validator=instance_of(bool))
    dmath_enable: bool = attr.ib(default=True, validator=instance_of(bool))
    dmath_allow_labels: bool = attr.ib(default=True, validator=instance_of(bool))
    dmath_allow_space: bool = attr.ib(default=True, validator=instance_of(bool))
    dmath_allow_digits: bool = attr.ib(default=True, validator=instance_of(bool))
    amsmath_enable: bool = attr.ib(default=False, validator=instance_of(bool))
    deflist_enable: bool = attr.ib(default=False, validator=instance_of(bool))

    update_mathjax: bool = attr.ib(default=True, validator=instance_of(bool))

    admonition_enable: bool = attr.ib(default=False, validator=instance_of(bool))
    figure_enable: bool = attr.ib(default=False, validator=instance_of(bool))

    disable_syntax: List[str] = attr.ib(
        factory=list,
        validator=deep_iterable(instance_of(str), instance_of((list, tuple))),
    )

    html_img_enable: bool = attr.ib(default=False, validator=instance_of(bool))

    # see https://en.wikipedia.org/wiki/List_of_URI_schemes
    url_schemes: Optional[List[str]] = attr.ib(
        default=None,
        validator=optional(deep_iterable(instance_of(str), instance_of((list, tuple)))),
    )

    heading_anchors: Optional[int] = attr.ib(
        default=None, validator=optional(in_([1, 2, 3, 4, 5, 6, 7]))
    )

    def as_dict(self, dict_factory=dict) -> dict:
        return attr.asdict(self, dict_factory=dict_factory)


def default_parser(config: MdParserConfig) -> MarkdownIt:
    """Return the default parser configuration for MyST"""
    if config.renderer == "sphinx":
        from myst_parser.sphinx_renderer import SphinxRenderer

        renderer_cls = SphinxRenderer
    elif config.renderer == "html":
        renderer_cls = RendererHTML
    elif config.renderer == "docutils":
        from myst_parser.docutils_renderer import DocutilsRenderer

        renderer_cls = DocutilsRenderer
    else:
        raise ValueError("unknown renderer type: {0}".format(config.renderer))

    if config.commonmark_only:
        md = MarkdownIt("commonmark", renderer_cls=renderer_cls)
        md.options.update({"commonmark_only": True})
        return md

    md = (
        MarkdownIt("commonmark", renderer_cls=renderer_cls)
        .enable("table")
        .use(front_matter_plugin)
        .use(myst_block_plugin)
        .use(myst_role_plugin)
        .use(footnote_plugin)
        .disable("footnote_inline")
        # disable this for now, because it need a new implementation in the renderer
        .disable("footnote_tail")
    )
    if config.dmath_enable:
        md.use(
            dollarmath_plugin,
            allow_labels=config.dmath_allow_labels,
            allow_space=config.dmath_allow_space,
            allow_digits=config.dmath_allow_digits,
        )
    if config.admonition_enable or config.figure_enable:
        # we don't want to yet remove un-referenced, because they may be referenced
        # in admonition type directives
        # so we do our own post processing
        md.use(container_plugin, "myst", validate=validate_container(config))
    if config.amsmath_enable:
        md.use(amsmath_plugin)
    if config.deflist_enable:
        md.use(deflist_plugin)
    if config.heading_anchors is not None:
        md.use(anchors_plugin, max_level=config.heading_anchors)
    for name in config.disable_syntax:
        md.disable(name, True)

    md.options.update(
        {
            "commonmark_only": False,
            "enable_html_img": config.html_img_enable,
            "myst_url_schemes": config.url_schemes,
            "enable_figures": config.figure_enable,
            "enable_anchors": config.heading_anchors is not None,
        }
    )

    return md


def validate_container(config: MdParserConfig):
    if config.admonition_enable:
        # NOTE with containers you can selectively only parse.
        # those that have a particular argument string.
        # However, this reduces the amount of feedback since, if you made an error
        # in the argument string, it would just ignore it rather than logging a warning
        def _validate_container(params: str, *args):
            return True

    elif config.figure_enable:

        def _validate_container(params: str, *args):
            return params.strip().startswith("{figure}") or params.strip().startswith(
                "{figure,"
            )

    return _validate_container


def to_docutils(
    text: str,
    parser_config: Optional[MdParserConfig] = None,
    options=None,
    env=None,
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
    :param document: the docutils root node to use (otherwise a new one will be created)
    :param in_sphinx_env: initialise a minimal sphinx environment (useful for testing)
    :param conf: the sphinx conf.py as a dictionary
    :param srcdir: to parse to the mock sphinc env

    :returns: docutils document
    """
    from myst_parser.docutils_renderer import make_document

    md = default_parser(parser_config or MdParserConfig())
    if options:
        md.options.update(options)
    md.options["document"] = document or make_document()
    if in_sphinx_env:
        from myst_parser.sphinx_renderer import mock_sphinx_env

        with mock_sphinx_env(conf=conf, srcdir=srcdir, document=md.options["document"]):
            return md.render(text, env)
    else:
        return md.render(text, env)


def to_html(text: str, env=None, config: Optional[MdParserConfig] = None):
    config = config or MdParserConfig()
    config.renderer = "html"
    md = default_parser(config)
    return md.render(text, env)


def to_tokens(text: str, env=None, config: Optional[MdParserConfig] = None):
    config = config or MdParserConfig()
    config.renderer = "html"
    md = default_parser(config)
    return md.parse(text, env)
