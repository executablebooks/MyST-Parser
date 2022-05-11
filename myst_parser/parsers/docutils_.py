"""MyST Markdown parser for docutils."""
from dataclasses import Field
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple, Union

from docutils import frontend, nodes
from docutils.core import default_description, publish_cmdline
from docutils.parsers.rst import Parser as RstParser
from typing_extensions import Literal, get_args, get_origin

from myst_parser.config.main import (
    MdParserConfig,
    TopmatterReadError,
    merge_file_level,
    read_topmatter,
)
from myst_parser.mdit_to_docutils.base import DocutilsRenderer, create_warning
from myst_parser.parsers.mdit import create_md_parser


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


class Unset:
    """A sentinel class for unset settings."""

    def __repr__(self):
        return "UNSET"


DOCUTILS_UNSET = Unset()
"""Sentinel for arguments not set through docutils.conf."""


DOCUTILS_EXCLUDED_ARGS = (
    # docutils.conf can't represent callables
    "heading_slug_func",
    # docutils.conf can't represent dicts
    "html_meta",
    "substitutions",
    # we can't add substitutions so not needed
    "sub_delimiters",
    # sphinx only options
    "heading_anchors",
    "ref_domains",
    "update_mathjax",
    "mathjax_classes",
)
"""Names of settings that cannot be set in docutils.conf."""


def _attr_to_optparse_option(at: Field, default: Any) -> Tuple[dict, str]:
    """Convert a field into a Docutils optparse options dict."""
    if at.type is int:
        return {"metavar": "<int>", "validator": _validate_int}, f"(default: {default})"
    if at.type is bool:
        return {
            "metavar": "<boolean>",
            "validator": frontend.validate_boolean,
        }, f"(default: {default})"
    if at.type is str:
        return {
            "metavar": "<str>",
        }, f"(default: '{default}')"
    if get_origin(at.type) is Literal and all(
        isinstance(a, str) for a in get_args(at.type)
    ):
        args = get_args(at.type)
        return {
            "metavar": f"<{'|'.join(repr(a) for a in args)}>",
            "type": "choice",
            "choices": args,
        }, f"(default: {default!r})"
    if at.type in (Iterable[str], Sequence[str]):
        return {
            "metavar": "<comma-delimited>",
            "validator": frontend.validate_comma_separated_list,
        }, f"(default: '{','.join(default)}')"
    if at.type == Tuple[str, str]:
        return {
            "metavar": "<str,str>",
            "validator": _create_validate_tuple(2),
        }, f"(default: '{','.join(default)}')"
    if at.type == Union[int, type(None)]:
        return {
            "metavar": "<null|int>",
            "validator": _validate_int,
        }, f"(default: {default})"
    if at.type == Union[Iterable[str], type(None)]:
        default_str = ",".join(default) if default else ""
        return {
            "metavar": "<null|comma-delimited>",
            "validator": frontend.validate_comma_separated_list,
        }, f"(default: {default_str!r})"
    raise AssertionError(
        f"Configuration option {at.name} not set up for use in docutils.conf."
    )


def attr_to_optparse_option(
    attribute: Field, default: Any, prefix: str = "myst_"
) -> Tuple[str, List[str], Dict[str, Any]]:
    """Convert an ``MdParserConfig`` attribute into a Docutils setting tuple.

    :returns: A tuple of ``(help string, option flags, optparse kwargs)``.
    """
    name = f"{prefix}{attribute.name}"
    flag = "--" + name.replace("_", "-")
    options = {"dest": name, "default": DOCUTILS_UNSET}
    at_options, type_str = _attr_to_optparse_option(attribute, default)
    options.update(at_options)
    help_str = attribute.metadata.get("help", "") if attribute.metadata else ""
    return (f"{help_str} {type_str}", [flag], options)


def create_myst_settings_spec(
    excluded: Sequence[str], config_cls=MdParserConfig, prefix: str = "myst_"
):
    """Return a list of Docutils setting for the docutils MyST section."""
    defaults = config_cls()
    return tuple(
        attr_to_optparse_option(at, getattr(defaults, at.name), prefix)
        for at in config_cls.get_fields()
        if at.name not in excluded
    )


def create_myst_config(
    settings: frontend.Values,
    excluded: Sequence[str],
    config_cls=MdParserConfig,
    prefix: str = "myst_",
):
    """Create a configuration instance from the given settings."""
    values = {}
    for attribute in config_cls.get_fields():
        if attribute.name in excluded:
            continue
        setting = f"{prefix}{attribute.name}"
        val = getattr(settings, setting, DOCUTILS_UNSET)
        if val is not DOCUTILS_UNSET:
            values[attribute.name] = val
    return config_cls(**values)


class Parser(RstParser):
    """Docutils parser for Markedly Structured Text (MyST)."""

    supported: Tuple[str, ...] = ("md", "markdown", "myst")
    """Aliases this parser supports."""

    settings_spec = (
        "MyST options",
        None,
        create_myst_settings_spec(DOCUTILS_EXCLUDED_ARGS),
        *RstParser.settings_spec,
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

        self.setup_parse(inputstring, document)

        # check for exorbitantly long lines
        if hasattr(document.settings, "line_length_limit"):
            for i, line in enumerate(inputstring.split("\n")):
                if len(line) > document.settings.line_length_limit:
                    error = document.reporter.error(
                        f"Line {i+1} exceeds the line-length-limit:"
                        f" {document.settings.line_length_limit}."
                    )
                    document.append(error)
                    return

        # create parsing configuration from the global config
        try:
            config = create_myst_config(document.settings, DOCUTILS_EXCLUDED_ARGS)
        except Exception as exc:
            error = document.reporter.error(f"Global myst configuration invalid: {exc}")
            document.append(error)
            config = MdParserConfig()

        # update the global config with the file-level config
        try:
            topmatter = read_topmatter(inputstring)
        except TopmatterReadError:
            pass  # this will be reported during the render
        else:
            if topmatter:
                warning = lambda wtype, msg: create_warning(  # noqa: E731
                    document, msg, line=1, append_to=document, subtype=wtype
                )
                config = merge_file_level(config, topmatter, warning)

        # parse content
        parser = create_md_parser(config, DocutilsRenderer)
        parser.options["document"] = document
        parser.render(inputstring)

        # post-processing

        # replace raw nodes if raw is not allowed
        if not getattr(document.settings, "raw_enabled", True):
            for node in document.traverse(nodes.raw):
                warning = document.reporter.warning("Raw content disabled.")
                node.parent.replace(node, warning)

        self.finish_parse()


def _run_cli(writer_name: str, writer_description: str, argv: Optional[List[str]]):
    """Run the command line interface for a particular writer."""
    publish_cmdline(
        parser=Parser(),
        writer_name=writer_name,
        description=(
            f"Generates {writer_description} from standalone MyST sources.\n{default_description}"
        ),
        argv=argv,
    )


def cli_html(argv: Optional[List[str]] = None) -> None:
    """Cmdline entrypoint for converting MyST to HTML."""
    _run_cli("html", "(X)HTML documents", argv)


def cli_html5(argv: Optional[List[str]] = None):
    """Cmdline entrypoint for converting MyST to HTML5."""
    _run_cli("html5", "HTML5 documents", argv)


def cli_latex(argv: Optional[List[str]] = None):
    """Cmdline entrypoint for converting MyST to LaTeX."""
    _run_cli("latex", "LaTeX documents", argv)


def cli_xml(argv: Optional[List[str]] = None):
    """Cmdline entrypoint for converting MyST to XML."""
    _run_cli("xml", "Docutils-native XML", argv)


def cli_pseudoxml(argv: Optional[List[str]] = None):
    """Cmdline entrypoint for converting MyST to pseudo-XML."""
    _run_cli("pseudoxml", "pseudo-XML", argv)
