"""A module for compatibility with the docutils>=0.17 `include` directive, in RST documents::

   .. include::
      :parser: myst_parser.docutils_
"""
from typing import Any, Callable, Iterable, Tuple, Union

from attr import Attribute
from docutils import frontend, nodes
from docutils.core import default_description, publish_cmdline
from docutils.parsers.rst import Parser as RstParser
from markdown_it.token import Token

from myst_parser.main import MdParserConfig, default_parser


def _validate_int(
    setting, value, option_parser, config_parser=None, config_section=None
) -> int:
    """Validate an integer setting."""
    return int(value)


def _create_validate_tuple(length: int) -> Callable[..., Tuple[str, ...]]:
    """Create a validator for a tuple of length `length`."""

    def _validate(
        setting, value, option_parser, config_parser=None, config_section=None
    ):
        string_list = frontend.validate_comma_separated_list(
            setting, value, option_parser, config_parser, config_section
        )
        if len(string_list) != length:
            raise ValueError(
                f"Expecting {length} items in {setting}, got {len(string_list)}."
            )
        return tuple(string_list)

    return _validate


DOCUTILS_UNSET = object()
"""Sentinel for arguments not set through docutils.conf."""


DOCUTILS_EXCLUDED_ARGS = (
    # docutils.conf can't represent callables
    "heading_slug_func",
    # docutils.conf can't represent dicts
    "html_meta",
    "substitutions",
    # we can't add substitutions so not needed
    "sub_delimiters",
    # We don't want to set the renderer from docutils.conf
    "renderer",
)
"""Names of settings that cannot be set in docutils.conf."""


def _docutils_optparse_options_of_attribute(
    at: Attribute, default: Any
) -> Tuple[dict, str]:
    """Convert an ``MdParserConfig`` attribute into a Docutils optparse options dict."""
    if at.type is int:
        return {"validator": _validate_int}, f"(type: int, default: {default})"
    if at.type is bool:
        return {
            "validator": frontend.validate_boolean
        }, f"(type: bool, default: {default})"
    if at.type is str:
        return {}, f"(type: str, default: '{default}')"
    if at.type == Iterable[str] or at.name == "url_schemes":
        return {
            "validator": frontend.validate_comma_separated_list
        }, f"(type: comma-delimited, default: '{','.join(default)}')"
    if at.type == Tuple[str, str]:
        return {
            "validator": _create_validate_tuple(2)
        }, f"(type: str,str, default: '{','.join(default)}')"
    if at.type == Union[int, type(None)] and at.default is None:
        return {
            "validator": _validate_int,
            "default": None,
        }, f"(type: null|int, default: {default})"
    if at.type == Union[Iterable[str], type(None)] and at.default is None:
        return {
            "validator": frontend.validate_comma_separated_list,
            "default": None,
        }, f"(type: comma-delimited, default: '{default or ','.join(default)}')"
    raise AssertionError(
        f"Configuration option {at.name} not set up for use in docutils.conf."
        f"Either add {at.name} to docutils_.DOCUTILS_EXCLUDED_ARGS,"
        "or add a new entry in _docutils_optparse_of_attribute."
    )


def _docutils_setting_tuple_of_attribute(
    attribute: Attribute, default: Any
) -> Tuple[str, Any, Any]:
    """Convert an ``MdParserConfig`` attribute into a Docutils setting tuple."""
    name = f"myst_{attribute.name}"
    flag = "--" + name.replace("_", "-")
    options = {"dest": name, "default": DOCUTILS_UNSET}
    at_options, type_str = _docutils_optparse_options_of_attribute(attribute, default)
    options.update(at_options)
    help_str = attribute.metadata.get("help", "") if attribute.metadata else ""
    return (f"{help_str} {type_str}", [flag], options)


def _myst_docutils_setting_tuples():
    defaults = MdParserConfig()
    return tuple(
        _docutils_setting_tuple_of_attribute(at, getattr(defaults, at.name))
        for at in MdParserConfig.get_fields()
        if at.name not in DOCUTILS_EXCLUDED_ARGS
    )


def create_myst_config(settings: frontend.Values):
    values = {}
    for attribute in MdParserConfig.get_fields():
        if attribute.name in DOCUTILS_EXCLUDED_ARGS:
            continue
        setting = f"myst_{attribute.name}"
        val = getattr(settings, setting)
        delattr(settings, setting)
        if val is not DOCUTILS_UNSET:
            values[attribute.name] = val
    values["renderer"] = "docutils"
    return MdParserConfig(**values)


class Parser(RstParser):
    """Docutils parser for Markedly Structured Text (MyST)."""

    supported: Tuple[str, ...] = ("md", "markdown", "myst")
    """Aliases this parser supports."""

    settings_spec = (
        *RstParser.settings_spec,
        "MyST options",
        None,
        _myst_docutils_setting_tuples(),
    )
    """Runtime settings specification."""

    config_section = "myst parser"
    config_section_dependencies = ("parsers",)
    translate_section_name = None

    def parse(self, inputstring: str, document: nodes.document) -> None:
        """Parse source text.

        :param inputstring: The source string to parse
        :param document: The root docutils node to add AST elements to
        """
        try:
            config = create_myst_config(document.settings)
        except (TypeError, ValueError) as error:
            document.reporter.error(f"myst configuration invalid: {error.args[0]}")
            config = MdParserConfig(renderer="docutils")
        parser = default_parser(config)
        parser.options["document"] = document
        env: dict = {}
        tokens = parser.parse(inputstring, env)
        if not tokens or tokens[0].type != "front_matter":
            # we always add front matter, so that we can merge it with global keys,
            # specified in the sphinx configuration
            tokens = [Token("front_matter", "", 0, content="{}", map=[0, 0])] + tokens
        parser.renderer.render(tokens, parser.options, env)


def cli_html():
    """Cmdline entrypoint for converting MyST to HTML."""
    publish_cmdline(
        parser=Parser(),
        writer_name="html",
        description=(
            f"Generates (X)HTML documents from standalone MyST sources.\n{default_description}"
        ),
    )


def cli_html5():
    """Cmdline entrypoint for converting MyST to HTML5."""
    publish_cmdline(
        parser=Parser(),
        writer_name="html5",
        description=(
            f"Generates HTML5 documents from standalone MyST sources.\n{default_description}"
        ),
    )


def cli_latex():
    """Cmdline entrypoint for converting MyST to LaTeX."""
    publish_cmdline(
        parser=Parser(),
        writer_name="latex",
        description=(
            f"Generates LaTeX documents from standalone MyST sources.\n{default_description}"
        ),
    )


def cli_xml():
    """Cmdline entrypoint for converting MyST to XML."""
    publish_cmdline(
        parser=Parser(),
        writer_name="xml",
        description=(
            f"Generates Docutils-native XML from standalone MyST sources.\n{default_description}"
        ),
    )


def cli_pseudoxml():
    """Cmdline entrypoint for converting MyST to pseudo-XML."""
    publish_cmdline(
        parser=Parser(),
        writer_name="pseudoxml",
        description=(
            f"Generates pseudo-XML from standalone MyST sources.\n{default_description}"
        ),
    )
