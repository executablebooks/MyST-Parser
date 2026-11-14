"""This module holds the ``create_md_parser`` function,
which creates a parser from the config.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from typing import TYPE_CHECKING

from markdown_it import MarkdownIt
from markdown_it.renderer import RendererProtocol
from markdown_it.rules_block import make_fence_rule
from mdit_py_plugins.amsmath import amsmath_plugin
from mdit_py_plugins.attrs import attrs_block_plugin, attrs_plugin
from mdit_py_plugins.deflist import deflist_plugin
from mdit_py_plugins.dollarmath import dollarmath_plugin
from mdit_py_plugins.field_list import fieldlist_plugin
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.gfm import gfm_plugin
from mdit_py_plugins.gfm_autolink import gfm_autolink_plugin
from mdit_py_plugins.myst_blocks import myst_block_plugin
from mdit_py_plugins.myst_role import myst_role_plugin
from mdit_py_plugins.section_ref import section_ref_plugin
from mdit_py_plugins.substitution import substitution_plugin
from mdit_py_plugins.wordcount import wordcount_plugin

from myst_parser.config.main import MdParserConfig

if TYPE_CHECKING:
    from docutils import nodes

DEFAULT_SMARTQUOTES: tuple[str, str, str, str] = (
    "\u201c",
    "\u201d",
    "\u2018",
    "\u2019",
)


def _coerce_quotes(quotes: Sequence[str]) -> tuple[str, str, str, str] | None:
    """Validate and normalize a 4-item quote sequence into a 4-tuple of strings."""
    if len(quotes) != 4:
        return None
    return (quotes[0], quotes[1], quotes[2], quotes[3])


def resolve_smartquotes(
    language_code: str | None = None,
    *,
    smart_quotes: bool | str = False,
    smartquotes_locales: Iterable[tuple[str, Sequence[str]]] | None = None,
) -> tuple[str, str, str, str]:
    """Resolve localized smart quote characters for ``markdown-it-py``.

    Follows Docutils' ``SmartQuotes`` locale lookup (``smartchars.quotes``,
    ``smartquotes_locales``, ``smart_quotes="alt"``, and BCP 47 subtag fallback
    via ``normalize_language_tag``) without mutating global Docutils state.
    Falls back to ``DEFAULT_SMARTQUOTES`` when ``language_code`` is unset or
    has no matching quote definition.

    :param language_code: Document language tag (e.g. ``"fr"``, ``"de_DE"``).
    :param smart_quotes: Docutils ``smart_quotes`` setting; strings starting
        with ``"alt"`` select the ``-x-altquot`` variant.
    :param smartquotes_locales: Optional ``(language_tag, quotes)`` overrides
        from Docutils' ``smartquotes_locales`` setting.
    :return: A 4-tuple ``(open_double, close_double, open_single, close_single)``.
    """
    if not language_code or not language_code.strip():
        return DEFAULT_SMARTQUOTES

    from docutils.utils import normalize_language_tag
    from docutils.utils.smartquotes import smartchars

    quotes_map: dict[str, Sequence[str]] = dict(smartchars.quotes)
    if smartquotes_locales:
        for locale_tag, locale_quotes in smartquotes_locales:
            coerced = _coerce_quotes(locale_quotes)
            if coerced is None or not locale_tag:
                continue
            normalized = normalize_language_tag(locale_tag)
            if normalized and normalized[0]:
                quotes_map[normalized[0]] = coerced

    lang = language_code.strip()
    if isinstance(smart_quotes, str) and smart_quotes.startswith("alt"):
        if "-x-altquot" in lang:
            lang = lang.replace("-x-altquot", "")
        else:
            lang = f"{lang}-x-altquot"

    for tag in normalize_language_tag(lang):
        if tag in quotes_map:
            coerced = _coerce_quotes(quotes_map[tag])
            if coerced is not None:
                return coerced

    return DEFAULT_SMARTQUOTES


def document_smartquotes(document: nodes.document, /) -> tuple[str, str, str, str]:
    """Resolve localized smart quote characters from a Docutils document.

    :param document: The Docutils document whose runtime settings are read.
    :return: A 4-tuple ``(open_double, close_double, open_single, close_single)``.
    """
    settings = document.settings
    return resolve_smartquotes(
        getattr(settings, "language_code", None),
        smart_quotes=getattr(settings, "smart_quotes", False),
        smartquotes_locales=getattr(settings, "smartquotes_locales", None),
    )


def linkify_available() -> bool:
    """Return whether the optional ``linkify-it-py`` dependency is installed."""
    # this is the same symbol that ``MarkdownIt`` consults internally
    from markdown_it.main import linkify_it

    return linkify_it is not None


def create_md_parser(
    config: MdParserConfig,
    renderer: Callable[[MarkdownIt], RendererProtocol],
    *,
    quotes: Sequence[str] | None = None,
) -> MarkdownIt:
    """Return a Markdown parser with the required MyST configuration.

    :param config: The MyST parser configuration.
    :param renderer: Renderer factory passed to ``MarkdownIt``.
    :param quotes: Optional 4-item sequence ``(open_double, close_double,
        open_single, close_single)`` overriding ``markdown-it-py``'s default
        typographic quote characters when ``smartquotes`` is enabled.
    :return: Configured ``MarkdownIt`` parser instance.
    """

    if config.commonmark_only:
        # see https://spec.commonmark.org/
        md = MarkdownIt("commonmark", renderer_cls=renderer).use(
            wordcount_plugin, per_minute=config.words_per_minute
        )
        md.options.update({"myst_config": config})
        return md

    if config.gfm_only:
        # see https://github.github.com/gfm/
        md = MarkdownIt("commonmark", renderer_cls=renderer)
        md.use(
            gfm_plugin,
            tasklists_editable=config.enable_checkboxes,
        )
        md.use(wordcount_plugin, per_minute=config.words_per_minute)
        md.options.update({"myst_config": config})
        return md

    md = (
        MarkdownIt("commonmark", renderer_cls=renderer)
        .enable("table")
        .use(front_matter_plugin)
        .use(myst_block_plugin)
        .use(myst_role_plugin)
        .use(footnote_plugin, inline=False, move_to_end=False, always_match_refs=True)
        .use(wordcount_plugin, per_minute=config.words_per_minute)
    )

    typographer = False
    if "smartquotes" in config.enable_extensions:
        md.enable("smartquotes")
        typographer = True
        if quotes is not None:
            coerced_quotes = _coerce_quotes(quotes)
            if coerced_quotes is None:
                raise ValueError("`quotes` must contain exactly 4 quote strings.")
            md.options["quotes"] = coerced_quotes
    if "replacements" in config.enable_extensions:
        md.enable("replacements")
        typographer = True
    linkify_enabled = False
    if "linkify" in config.enable_extensions and md.linkify is not None:
        # if linkify-it-py is not installed, the extension is simply disabled here;
        # a warning is emitted by the sphinx/docutils parsers (see linkify_available)
        md.enable("linkify")
        md.linkify.set({"fuzzy_link": config.linkify_fuzzy_links})
        linkify_enabled = True
    if "gfm_autolink" in config.enable_extensions:
        md.use(gfm_autolink_plugin)
    if "section_ref" in config.enable_extensions:
        md.use(section_ref_plugin)
    if "strikethrough" in config.enable_extensions:
        md.enable("strikethrough")
        md.options["strikethrough_single_tilde"] = config.strikethrough_single_tilde
    if "dollarmath" in config.enable_extensions:
        md.use(
            dollarmath_plugin,
            allow_labels=config.dmath_allow_labels,
            allow_space=config.dmath_allow_space,
            allow_digits=config.dmath_allow_digits,
            double_inline=config.dmath_double_inline,
        )
    if "colon_fence" in config.enable_extensions:
        colon_fence = make_fence_rule(
            markers=(":",),
            token_type="colon_fence",
            exact_match=config.colon_fence_exact_match,
        )
        md.block.ruler.before(
            "fence",
            "colon_fence",
            colon_fence,
            {"alt": ["paragraph", "reference", "blockquote", "list", "footnote_def"]},
        )
    if "amsmath" in config.enable_extensions:
        md.use(amsmath_plugin)
    if "deflist" in config.enable_extensions:
        md.use(deflist_plugin)
    if "fieldlist" in config.enable_extensions:
        md.use(fieldlist_plugin)
    if "tasklist" in config.enable_extensions:
        md.options["tasklists"] = True
        md.options["tasklists_editable"] = config.enable_checkboxes
    if "alert" in config.enable_extensions:
        md.options["alerts"] = True
    if "substitution" in config.enable_extensions:
        md.use(substitution_plugin, *config.sub_delimiters)
    if "attrs_inline" in config.enable_extensions:
        md.use(
            attrs_plugin,
            after=("image", "code_inline", "link_close", "span_close"),
            spans=True,
            span_after="footnote_ref",
        )
    elif "attrs_image" in config.enable_extensions:
        # TODO deprecate
        md.use(attrs_plugin, after=("image",))
    if "attrs_block" in config.enable_extensions:
        md.use(attrs_block_plugin)
    for name in config.disable_syntax:
        md.disable(name, True)

    md.options.update(
        {
            "typographer": typographer,
            "linkify": linkify_enabled,
            "myst_config": config,
        }
    )

    return md
