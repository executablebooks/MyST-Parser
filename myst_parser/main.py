from typing import Dict, Iterable, List, Optional, Tuple

import attr
from attr.validators import deep_iterable, deep_mapping, in_, instance_of, optional

from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML

from mdit_py_plugins.amsmath import amsmath_plugin
from mdit_py_plugins.anchors import anchors_plugin
from mdit_py_plugins.deflist import deflist_plugin
from mdit_py_plugins.colon_fence import colon_fence_plugin
from mdit_py_plugins.dollarmath import dollarmath_plugin
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.myst_blocks import myst_block_plugin
from mdit_py_plugins.myst_role import myst_role_plugin
from mdit_py_plugins.substitution import substitution_plugin

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
    dmath_allow_labels: bool = attr.ib(default=True, validator=instance_of(bool))
    dmath_allow_space: bool = attr.ib(default=True, validator=instance_of(bool))
    dmath_allow_digits: bool = attr.ib(default=True, validator=instance_of(bool))

    update_mathjax: bool = attr.ib(default=True, validator=instance_of(bool))

    # TODO remove deprecated _enable attributes after v0.13.0
    admonition_enable: bool = attr.ib(
        default=False, validator=instance_of(bool), repr=False
    )
    figure_enable: bool = attr.ib(
        default=False, validator=instance_of(bool), repr=False
    )
    dmath_enable: bool = attr.ib(default=False, validator=instance_of(bool), repr=False)
    amsmath_enable: bool = attr.ib(
        default=False, validator=instance_of(bool), repr=False
    )
    deflist_enable: bool = attr.ib(
        default=False, validator=instance_of(bool), repr=False
    )
    html_img_enable: bool = attr.ib(
        default=False, validator=instance_of(bool), repr=False
    )
    colon_fence_enable: bool = attr.ib(
        default=False, validator=instance_of(bool), repr=False
    )

    enable_extensions: Iterable[str] = attr.ib(factory=lambda: ["dollarmath"])

    @enable_extensions.validator
    def check_extensions(self, attribute, value):
        if not isinstance(value, Iterable):
            raise TypeError(f"myst_enable_extensions not iterable: {value}")
        diff = set(value).difference(
            [
                "dollarmath",
                "amsmath",
                "deflist",
                "html_image",
                "colon_fence",
                "smartquotes",
                "replacements",
                "linkify",
                "substitution",
            ]
        )
        if diff:
            raise ValueError(f"myst_enable_extensions not recognised: {diff}")

    disable_syntax: List[str] = attr.ib(
        factory=list,
        validator=deep_iterable(instance_of(str), instance_of((list, tuple))),
    )

    # see https://en.wikipedia.org/wiki/List_of_URI_schemes
    url_schemes: Optional[List[str]] = attr.ib(
        default=None,
        validator=optional(deep_iterable(instance_of(str), instance_of((list, tuple)))),
    )

    heading_anchors: Optional[int] = attr.ib(
        default=None, validator=optional(in_([1, 2, 3, 4, 5, 6, 7]))
    )

    substitutions: Dict[str, str] = attr.ib(
        factory=dict,
        validator=deep_mapping(instance_of(str), instance_of(str), instance_of(dict)),
    )

    sub_delimiters: Tuple[str, str] = attr.ib(default=("{", "}"))

    @sub_delimiters.validator
    def check_sub_delimiters(self, attribute, value):
        if (not isinstance(value, (tuple, list))) or len(value) != 2:
            raise TypeError(f"myst_sub_delimiters is not a tuple of length 2: {value}")
        for delim in value:
            if (not isinstance(delim, str)) or len(delim) != 1:
                raise TypeError(
                    f"myst_sub_delimiters does not contain strings of length 1: {value}"
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

    typographer = False
    if "smartquotes" in config.enable_extensions:
        md.enable("smartquotes")
        typographer = True
    if "replacements" in config.enable_extensions:
        md.enable("replacements")
        typographer = True
    if "linkify" in config.enable_extensions:
        # TODO warn, don't enable, if linkify-it-py not installed
        md.enable("linkify")

    if "dollarmath" in config.enable_extensions:
        md.use(
            dollarmath_plugin,
            allow_labels=config.dmath_allow_labels,
            allow_space=config.dmath_allow_space,
            allow_digits=config.dmath_allow_digits,
        )
    if "colon_fence" in config.enable_extensions:
        md.use(colon_fence_plugin)
    if "amsmath" in config.enable_extensions:
        md.use(amsmath_plugin)
    if "deflist" in config.enable_extensions:
        md.use(deflist_plugin)
    if "substitution" in config.enable_extensions:
        md.use(substitution_plugin, *config.sub_delimiters)
    if config.heading_anchors is not None:
        md.use(anchors_plugin, max_level=config.heading_anchors)
    for name in config.disable_syntax:
        md.disable(name, True)

    md.options.update(
        {
            "commonmark_only": False,
            "typographer": typographer,
            "linkify": "linkify" in config.enable_extensions,
            "enable_html_img": "html_image" in config.enable_extensions,
            "myst_url_schemes": config.url_schemes,
            "enable_anchors": config.heading_anchors is not None,
            "substitutions": config.substitutions,
        }
    )

    return md


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
