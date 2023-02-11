"""MyST Markdown parser for docutils."""
from dataclasses import Field
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)

import yaml
from docutils import frontend, nodes
from docutils.core import default_description, publish_cmdline
from docutils.parsers.rst import Parser as RstParser

from myst_parser._compat import Literal, get_args, get_origin
from myst_parser.config.main import (
    MdParserConfig,
    TopmatterReadError,
    merge_file_level,
    read_topmatter,
)
from myst_parser.mdit_to_docutils.base import DocutilsRenderer
from myst_parser.parsers.mdit import create_md_parser
from myst_parser.warnings_ import MystWarnings, create_warning


def _validate_int(
    setting, value, option_parser, config_parser=None, config_section=None
) -> int:
    """Validate an integer setting."""
    return int(value)


def _validate_comma_separated_set(
    setting, value, option_parser, config_parser=None, config_section=None
) -> Set[str]:
    """Validate an integer setting."""
    value = frontend.validate_comma_separated_list(
        setting, value, option_parser, config_parser, config_section
    )
    return set(value)


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

    def __bool__(self):
        # this allows to check if the setting is unset/falsy
        return False


DOCUTILS_UNSET = Unset()
"""Sentinel for arguments not set through docutils.conf."""


def _create_validate_yaml(field: Field):
    """Create a deserializer/validator for a json setting."""

    def _validate_yaml(
        setting, value, option_parser, config_parser=None, config_section=None
    ):
        """Check/normalize a key-value pair setting.

        Items delimited by `,`, and key-value pairs delimited by `=`.
        """
        try:
            output = yaml.safe_load(value)
        except Exception:
            raise ValueError("Invalid YAML string")
        if not isinstance(output, dict):
            raise ValueError("Expecting a YAML dictionary")
        return output

    return _validate_yaml


def _validate_url_schemes(
    setting, value, option_parser, config_parser=None, config_section=None
):
    """Validate a url_schemes setting.

    This is a tricky one, because it can be either a comma-separated list or a YAML dictionary.
    """
    try:
        output = yaml.safe_load(value)
    except Exception:
        raise ValueError("Invalid YAML string")
    if isinstance(output, str):
        output = {k: None for k in output.split(",")}
    if not isinstance(output, dict):
        raise ValueError("Expecting a comma-delimited str or YAML dictionary")
    return output


def _attr_to_optparse_option(at: Field, default: Any) -> Tuple[dict, str]:
    """Convert a field into a Docutils optparse options dict.

    :returns: (option_dict, default)
    """
    if at.name == "url_schemes":
        return {
            "metavar": "<comma-delimited>|<yaml-dict>",
            "validator": _validate_url_schemes,
        }, ",".join(default)
    if at.type is int:
        return {"metavar": "<int>", "validator": _validate_int}, str(default)
    if at.type is bool:
        return {
            "metavar": "<boolean>",
            "validator": frontend.validate_boolean,
        }, str(default)
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
        }, repr(default)
    if at.type in (Iterable[str], Sequence[str]):
        return {
            "metavar": "<comma-delimited>",
            "validator": frontend.validate_comma_separated_list,
        }, ",".join(default)
    if at.type == Set[str]:
        return {
            "metavar": "<comma-delimited>",
            "validator": _validate_comma_separated_set,
        }, ",".join(default)
    if at.type == Tuple[str, str]:
        return {
            "metavar": "<str,str>",
            "validator": _create_validate_tuple(2),
        }, ",".join(default)
    if at.type == Union[int, type(None)]:
        return {
            "metavar": "<null|int>",
            "validator": _validate_int,
        }, str(default)
    if at.type == Union[Iterable[str], type(None)]:
        return {
            "metavar": "<null|comma-delimited>",
            "validator": frontend.validate_comma_separated_list,
        }, ",".join(default) if default else ""
    if get_origin(at.type) is dict:
        return {
            "metavar": "<yaml-dict>",
            "validator": _create_validate_yaml(at),
        }, str(default) if default else ""
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
    at_options, default_str = _attr_to_optparse_option(attribute, default)
    options.update(at_options)
    help_str = attribute.metadata.get("help", "") if attribute.metadata else ""
    if default_str:
        help_str += f" (default: {default_str})"
    return (help_str, [flag], options)


def create_myst_settings_spec(config_cls=MdParserConfig, prefix: str = "myst_"):
    """Return a list of Docutils setting for the docutils MyST section."""
    defaults = config_cls()
    return tuple(
        attr_to_optparse_option(at, getattr(defaults, at.name), prefix)
        for at in config_cls.get_fields()
        if ("docutils" not in at.metadata.get("omit", []))
    )


def create_myst_config(
    settings: frontend.Values,
    config_cls=MdParserConfig,
    prefix: str = "myst_",
):
    """Create a configuration instance from the given settings."""
    values = {}
    for attribute in config_cls.get_fields():
        if "docutils" in attribute.metadata.get("omit", []):
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
        create_myst_settings_spec(),
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
            config = create_myst_config(document.settings)
        except Exception as exc:
            error = document.reporter.error(f"Global myst configuration invalid: {exc}")
            document.append(error)
            config = MdParserConfig()

        if "attrs_image" in config.enable_extensions:
            create_warning(
                document,
                "The `attrs_image` extension is deprecated, "
                "please use `attrs_inline` instead.",
                MystWarnings.DEPRECATED,
            )

        # update the global config with the file-level config
        try:
            topmatter = read_topmatter(inputstring)
        except TopmatterReadError:
            pass  # this will be reported during the render
        else:
            if topmatter:
                warning = lambda wtype, msg: create_warning(  # noqa: E731
                    document, msg, wtype, line=1, append_to=document
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
