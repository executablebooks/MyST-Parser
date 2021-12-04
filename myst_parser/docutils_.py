"""A module for compatibility with the docutils>=0.17 `include` directive, in RST documents::

   .. include::
      :parser: myst_parser.docutils_
"""
from typing import Iterable, Tuple, Union

from attr import Attribute
from docutils import frontend, nodes
from docutils.parsers.rst import Parser as RstParser
from markdown_it.token import Token

from myst_parser.main import MdParserConfig, default_parser


def validate_int(
    setting, value, option_parser, config_parser=None, config_section=None
):
    return int(value)


def validate_tuple(length: int):
    def validate(
        setting, value, option_parser, config_parser=None, config_section=None
    ):
        l = frontend.validate_comma_separated_list(
            setting, value, option_parser, config_parser, config_section
        )
        if len(l) != length:
            MSG = "Expecting {} items in {}, got {}: {}."
            raise ValueError(MSG.format(length, setting, len(l)))
        return tuple(l)

    return validate


DOCUTILS_UNSET = object()
"""Sentinel for arguments not set through docutils.conf."""

DOCUTILS_OPTPARSE_OVERRIDES = {
    "url_schemes": {"validator": frontend.validate_comma_separated_list},
    # url_schemes accepts an iterable or ``None``, but ``None`` is the same as ``()``.
}
"""Custom optparse configurations for docutils.conf entries."""

DOCUTILS_EXCLUDED_ARGS = (
    # docutils.conf can't represent callables
    "heading_slug_func",
    # docutils.conf can't represent dicts
    "html_meta",
    "substitutions",
    # We don't want to set the renderer from docutils.conf
    "renderer",
)
"""Names of settings that cannot be set in docutils.conf."""


def _docutils_optparse_options_of_attribute(a: Attribute):
    override = DOCUTILS_OPTPARSE_OVERRIDES.get(a.name)
    if override is not None:
        return override
    if a.type is int:
        return {"validator": validate_int}
    if a.type is bool:
        return {"validator": frontend.validate_boolean}
    if a.type is str:
        return {}
    if a.type == Iterable[str]:
        return {"validator": frontend.validate_comma_separated_list}
    if a.type == Tuple[str, str]:
        return {"validator": validate_tuple(2)}
    if a.type == Union[int, type(None)] and a.default is None:
        return {"validator": validate_int, "default": None}
    if a.type == Union[Iterable[str], type(None)] and a.default is None:
        return {"validator": frontend.validate_comma_separated_list, "default": None}
    raise AssertionError(
        f"""Configuration option {a.name} not set up for use \
in docutils.conf.  Either add {a.name} to docutils_.DOCUTILS_EXCLUDED_ARGS, or \
add a new entry in _docutils_optparse_of_attribute."""
    )


def _docutils_setting_tuple_of_attribute(attribute):
    """Convert an ``MdParserConfig`` attribute into a Docutils setting tuple."""
    name = "myst_" + attribute.name
    flag = "--" + name.replace("_", "-")
    options = {"dest": name, "default": DOCUTILS_UNSET}
    options.update(_docutils_optparse_options_of_attribute(attribute))
    return (None, [flag], options)


def _myst_docutils_setting_tuples():
    return tuple(
        _docutils_setting_tuple_of_attribute(a)
        for a in MdParserConfig.get_fields()
        if not a.name in DOCUTILS_EXCLUDED_ARGS
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


if __name__ == "__main__":
    from docutils.core import default_description, publish_cmdline

    publish_cmdline(
        parser=Parser(),
        writer_name="html",
        description="Generates (X)HTML documents from standalone MyST sources.  "
        + default_description,
    )
