"""This module holds the global configuration for the parser ``MdParserConfig``,
and the ``create_md_parser`` function, which creates a parser from the config.
"""
from typing import Any, Callable, Dict, Iterable, Optional, Sequence, Tuple, Union, cast

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
from mdit_py_plugins.field_list import fieldlist_plugin
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

    commonmark_only: bool = attr.ib(
        default=False,
        validator=instance_of(bool),
        metadata={"help": "Use strict CommonMark parser"},
    )
    gfm_only: bool = attr.ib(
        default=False,
        validator=instance_of(bool),
        metadata={"help": "Use strict Github Flavoured Markdown parser"},
    )
    enable_extensions: Sequence[str] = attr.ib(
        factory=list, metadata={"help": "Enable extensions"}
    )

    linkify_fuzzy_links: bool = attr.ib(
        default=True,
        validator=instance_of(bool),
        metadata={"help": "linkify: recognise URLs without schema prefixes"},
    )

    dmath_allow_labels: bool = attr.ib(
        default=True,
        validator=instance_of(bool),
        metadata={"help": "Parse `$$...$$ (label)`"},
    )
    dmath_allow_space: bool = attr.ib(
        default=True,
        validator=instance_of(bool),
        metadata={"help": "dollarmath: allow initial/final spaces in `$ ... $`"},
    )
    dmath_allow_digits: bool = attr.ib(
        default=True,
        validator=instance_of(bool),
        metadata={"help": "dollarmath: allow initial/final digits `1$ ...$2`"},
    )
    dmath_double_inline: bool = attr.ib(
        default=False,
        validator=instance_of(bool),
        metadata={"help": "dollarmath: parse inline `$$ ... $$`"},
    )

    update_mathjax: bool = attr.ib(
        default=True,
        validator=instance_of(bool),
        metadata={"help": "Update sphinx.ext.mathjax configuration"},
    )

    mathjax_classes: str = attr.ib(
        default="tex2jax_process|mathjax_process|math|output_area",
        validator=instance_of(str),
        metadata={"help": "MathJax classes to add to math HTML"},
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
                "fieldlist",
                "html_admonition",
                "html_image",
                "colon_fence",
                "smartquotes",
                "replacements",
                "linkify",
                "strikethrough",
                "substitution",
                "tasklist",
            ]
        )
        if diff:
            raise ValueError(f"myst_enable_extensions not recognised: {diff}")

    disable_syntax: Iterable[str] = attr.ib(
        factory=list,
        validator=deep_iterable(instance_of(str), instance_of((list, tuple))),
        metadata={"help": "Disable syntax elements"},
    )

    all_links_external: bool = attr.ib(
        default=False,
        validator=instance_of(bool),
        metadata={"help": "Parse all links as simple hyperlinks"},
    )

    # see https://en.wikipedia.org/wiki/List_of_URI_schemes
    url_schemes: Optional[Iterable[str]] = attr.ib(
        default=cast(Optional[Iterable[str]], ("http", "https", "mailto", "ftp")),
        validator=optional(deep_iterable(instance_of(str), instance_of((list, tuple)))),
        metadata={"help": "URL scheme prefixes identified as external links"},
    )

    ref_domains: Optional[Iterable[str]] = attr.ib(
        default=None,
        validator=optional(deep_iterable(instance_of(str), instance_of((list, tuple)))),
        metadata={"help": "Sphinx domain names to search in for references"},
    )

    highlight_code_blocks: bool = attr.ib(
        default=True,
        validator=instance_of(bool),
        metadata={
            "help": "Syntax highlight code blocks with pygments",
            "docutils_only": True,
        },
    )

    number_code_blocks: Sequence[str] = attr.ib(
        default=(),
        validator=deep_iterable(instance_of(str)),
        metadata={"help": "Add line numbers to code blocks with these languages"},
    )

    title_to_header: bool = attr.ib(
        default=False,
        validator=instance_of(bool),
        metadata={"help": "Convert a `title` field in the top-matter to a H1 header"},
    )

    heading_anchors: Optional[int] = attr.ib(
        default=None,
        validator=optional(in_([1, 2, 3, 4, 5, 6, 7])),
        metadata={"help": "Heading level depth to assign HTML anchors"},
    )

    heading_slug_func: Optional[Callable[[str], str]] = attr.ib(
        default=None,
        validator=optional(is_callable()),
        metadata={"help": "Function for creating heading anchors"},
    )

    html_meta: Dict[str, str] = attr.ib(
        factory=dict,
        validator=deep_mapping(instance_of(str), instance_of(str), instance_of(dict)),
        repr=lambda v: str(list(v)),
        metadata={"help": "HTML meta tags"},
    )

    footnote_transition: bool = attr.ib(
        default=True,
        validator=instance_of(bool),
        metadata={"help": "Place a transition before any footnotes"},
    )

    substitutions: Dict[str, Union[str, int, float]] = attr.ib(
        factory=dict,
        validator=deep_mapping(
            instance_of(str), instance_of((str, int, float)), instance_of(dict)
        ),
        repr=lambda v: str(list(v)),
        metadata={"help": "Substitutions"},
    )

    sub_delimiters: Tuple[str, str] = attr.ib(
        default=("{", "}"), metadata={"help": "Substitution delimiters"}
    )

    words_per_minute: int = attr.ib(
        default=200,
        validator=instance_of(int),
        metadata={"help": "For reading speed calculations"},
    )

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
        """Return all attribute fields in this class."""
        return attr.fields(cls)

    def as_dict(self, dict_factory=dict) -> dict:
        """Return a dictionary of field name -> value."""
        return attr.asdict(self, dict_factory=dict_factory)

    def as_triple(self) -> Iterable[Tuple[str, Any, attr.Attribute]]:
        """Yield triples of (name, value, field)."""
        fields = attr.fields_dict(self.__class__)
        for name, value in attr.asdict(self).items():
            yield name, value, fields[name]


def default_parser(config: MdParserConfig):
    raise NotImplementedError(
        "default_parser has been deprecated and replaced by create_md_parser."
        "You must also supply the renderer class directly to create_md_parser."
    )


def create_md_parser(
    config: MdParserConfig, renderer: Callable[[MarkdownIt], RendererProtocol]
) -> MarkdownIt:
    """Return a Markdown parser with the required MyST configuration."""

    # TODO warn if linkify required and linkify-it-py not installed
    # (currently the parse will unceremoniously except)

    if config.commonmark_only:
        # see https://spec.commonmark.org/
        md = MarkdownIt("commonmark", renderer_cls=renderer).use(
            wordcount_plugin, per_minute=config.words_per_minute
        )
        md.options.update({"myst_config": config})
        return md

    if config.gfm_only:
        # see https://github.github.com/gfm/
        md = (
            MarkdownIt("commonmark", renderer_cls=renderer)
            # note, strikethrough currently only supported tentatively for HTML
            .enable("strikethrough")
            .enable("table")
            .use(tasklists_plugin)
            .enable("linkify")
            .use(wordcount_plugin, per_minute=config.words_per_minute)
        )
        md.options.update({"linkify": True, "myst_config": config})
        return md

    md = (
        MarkdownIt("commonmark", renderer_cls=renderer)
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
        md.enable("linkify")
        if md.linkify is not None:
            md.linkify.set({"fuzzy_link": config.linkify_fuzzy_links})
    if "strikethrough" in config.enable_extensions:
        md.enable("strikethrough")
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
    if "fieldlist" in config.enable_extensions:
        md.use(fieldlist_plugin)
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
            "typographer": typographer,
            "linkify": "linkify" in config.enable_extensions,
            "myst_config": config,
        }
    )

    return md


def to_docutils(
    text: str,
    parser_config: Optional[MdParserConfig] = None,
    *,
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
    from myst_parser.sphinx_renderer import SphinxRenderer

    md = create_md_parser(parser_config or MdParserConfig(), SphinxRenderer)
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
    """Render text to HTML directly using markdown-it-py.

    This is mainly for test purposes only.
    """
    config = config or MdParserConfig()
    md = create_md_parser(config, RendererHTML)
    return md.render(text, env)


def to_tokens(text: str, env=None, config: Optional[MdParserConfig] = None):
    config = config or MdParserConfig()
    md = create_md_parser(config, RendererHTML)
    return md.parse(text, env)
