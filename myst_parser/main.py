from typing import Callable, Dict, Iterable, Optional, Tuple, Union, cast

import attr
from attr.validators import (
    deep_iterable,
    deep_mapping,
    in_,
    instance_of,
    is_callable,
    optional,
)
from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML, RendererProtocol
from mdit_py_plugins.amsmath import amsmath_plugin
from mdit_py_plugins.anchors import anchors_plugin
from mdit_py_plugins.colon_fence import colon_fence_plugin
from mdit_py_plugins.deflist import deflist_plugin
from mdit_py_plugins.dollarmath import dollarmath_plugin
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.myst_blocks import myst_block_plugin
from mdit_py_plugins.myst_role import myst_role_plugin
from mdit_py_plugins.substitution import substitution_plugin
from mdit_py_plugins.tasklists import tasklists_plugin
from mdit_py_plugins.wordcount import wordcount_plugin

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
    enable_extensions: Iterable[str] = attr.ib(factory=lambda: ["dollarmath"])

    dmath_allow_labels: bool = attr.ib(default=True, validator=instance_of(bool))
    dmath_allow_space: bool = attr.ib(default=True, validator=instance_of(bool))
    dmath_allow_digits: bool = attr.ib(default=True, validator=instance_of(bool))
    dmath_double_inline: bool = attr.ib(default=False, validator=instance_of(bool))

    update_mathjax: bool = attr.ib(default=True, validator=instance_of(bool))

    mathjax_classes: str = attr.ib(
        default="tex2jax_process|mathjax_process|math",
        validator=instance_of(str),
    )

    @enable_extensions.validator
    def check_extensions(self, attribute, value):
        if not isinstance(value, Iterable):
            raise TypeError(f"myst_enable_extensions not iterable: {value}")
        diff = set(value).difference(
            [
                "dollarmath",
                "amsmath",
                "deflist",
                "html_admonition",
                "html_image",
                "colon_fence",
                "smartquotes",
                "replacements",
                "linkify",
                "substitution",
                "tasklist",
            ]
        )
        if diff:
            raise ValueError(f"myst_enable_extensions not recognised: {diff}")

    disable_syntax: Iterable[str] = attr.ib(
        factory=list,
        validator=deep_iterable(instance_of(str), instance_of((list, tuple))),
    )

    # see https://en.wikipedia.org/wiki/List_of_URI_schemes
    url_schemes: Optional[Iterable[str]] = attr.ib(
        default=cast(Optional[Iterable[str]], ("http", "https", "mailto", "ftp")),
        validator=optional(deep_iterable(instance_of(str), instance_of((list, tuple)))),
    )

    heading_anchors: Optional[int] = attr.ib(
        default=None, validator=optional(in_([1, 2, 3, 4, 5, 6, 7]))
    )

    heading_slug_func: Optional[Callable[[str], str]] = attr.ib(
        default=None, validator=optional(is_callable())
    )

    html_meta: Dict[str, str] = attr.ib(
        factory=dict,
        validator=deep_mapping(instance_of(str), instance_of(str), instance_of(dict)),
        repr=lambda v: str(list(v)),
    )

    footnote_transition: bool = attr.ib(default=True, validator=instance_of(bool))

    substitutions: Dict[str, Union[str, int, float]] = attr.ib(
        factory=dict,
        validator=deep_mapping(
            instance_of(str), instance_of((str, int, float)), instance_of(dict)
        ),
        repr=lambda v: str(list(v)),
    )

    sub_delimiters: Tuple[str, str] = attr.ib(default=("{", "}"))

    words_per_minute: int = attr.ib(default=200, validator=instance_of(int))

    @sub_delimiters.validator
    def check_sub_delimiters(self, attribute, value):
        if (not isinstance(value, (tuple, list))) or len(value) != 2:
            raise TypeError(f"myst_sub_delimiters is not a tuple of length 2: {value}")
        for delim in value:
            if (not isinstance(delim, str)) or len(delim) != 1:
                raise TypeError(
                    f"myst_sub_delimiters does not contain strings of length 1: {value}"
                )

    @classmethod
    def get_fields(cls) -> Tuple[attr.Attribute, ...]:
        return attr.fields(cls)

    def as_dict(self, dict_factory=dict) -> dict:
        return attr.asdict(self, dict_factory=dict_factory)


def default_parser(config: MdParserConfig) -> MarkdownIt:
    """Return the default parser configuration for MyST"""
    renderer_cls: Callable[[MarkdownIt], RendererProtocol]

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
        md = MarkdownIt("commonmark", renderer_cls=renderer_cls).use(
            wordcount_plugin, per_minute=config.words_per_minute
        )
        md.options.update({"commonmark_only": True})
        return md

    md = (
        MarkdownIt("commonmark", renderer_cls=renderer_cls)
        .enable("table")
        .use(front_matter_plugin)
        .use(myst_block_plugin)
        .use(myst_role_plugin)
        .use(footnote_plugin)
        .use(wordcount_plugin, per_minute=config.words_per_minute)
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
            double_inline=config.dmath_double_inline,
        )
    if "colon_fence" in config.enable_extensions:
        md.use(colon_fence_plugin)
    if "amsmath" in config.enable_extensions:
        md.use(amsmath_plugin)
    if "deflist" in config.enable_extensions:
        md.use(deflist_plugin)
    if "tasklist" in config.enable_extensions:
        md.use(tasklists_plugin)
    if "substitution" in config.enable_extensions:
        md.use(substitution_plugin, *config.sub_delimiters)
    if config.heading_anchors is not None:
        md.use(
            anchors_plugin,
            max_level=config.heading_anchors,
            slug_func=config.heading_slug_func,
        )
    for name in config.disable_syntax:
        md.disable(name, True)

    md.options.update(
        {
            # standard options
            "typographer": typographer,
            "linkify": "linkify" in config.enable_extensions,
            # myst options
            "commonmark_only": False,
            "myst_extensions": set(
                list(config.enable_extensions)
                + (["heading_anchors"] if config.heading_anchors is not None else [])
            ),
            "myst_url_schemes": config.url_schemes,
            "myst_substitutions": config.substitutions,
            "myst_html_meta": config.html_meta,
            "myst_footnote_transition": config.footnote_transition,
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
    """Render text to the docutils AST (before transforms)

    :param text: the text to render
    :param options: options to update the parser with
    :param env: The sandbox environment for the parse
        (will contain e.g. reference definitions)
    :param document: the docutils root node to use (otherwise a new one will be created)
    :param in_sphinx_env: initialise a minimal sphinx environment (useful for testing)
    :param conf: the sphinx conf.py as a dictionary
    :param srcdir: to parse to the mock sphinx env

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
