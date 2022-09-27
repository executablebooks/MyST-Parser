"""The configuration for the myst parser."""
import dataclasses as dc
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    Optional,
    Sequence,
    Tuple,
    Union,
    cast,
)

from .dc_validators import (
    deep_iterable,
    deep_mapping,
    in_,
    instance_of,
    is_callable,
    optional,
    validate_field,
    validate_fields,
)


def check_extensions(_, __, value):
    if not isinstance(value, Iterable):
        raise TypeError(f"'enable_extensions' not iterable: {value}")
    diff = set(value).difference(
        [
            "amsmath",
            "attrs_image",
            "colon_fence",
            "deflist",
            "dollarmath",
            "fieldlist",
            "html_admonition",
            "html_image",
            "linkify",
            "replacements",
            "smartquotes",
            "strikethrough",
            "substitution",
            "tasklist",
        ]
    )
    if diff:
        raise ValueError(f"'enable_extensions' items not recognised: {diff}")


def check_sub_delimiters(_, __, value):
    if (not isinstance(value, (tuple, list))) or len(value) != 2:
        raise TypeError(f"myst_sub_delimiters is not a tuple of length 2: {value}")
    for delim in value:
        if (not isinstance(delim, str)) or len(delim) != 1:
            raise TypeError(
                f"myst_sub_delimiters does not contain strings of length 1: {value}"
            )


@dc.dataclass()
class MdParserConfig:
    """Configuration options for the Markdown Parser.

    Note in the sphinx configuration these option names are prepended with ``myst_``
    """

    # TODO replace commonmark_only, gfm_only with a single option

    commonmark_only: bool = dc.field(
        default=False,
        metadata={
            "validator": instance_of(bool),
            "help": "Use strict CommonMark parser",
        },
    )
    gfm_only: bool = dc.field(
        default=False,
        metadata={
            "validator": instance_of(bool),
            "help": "Use strict Github Flavoured Markdown parser",
        },
    )

    enable_extensions: Sequence[str] = dc.field(
        default_factory=list,
        metadata={"validator": check_extensions, "help": "Enable syntax extensions"},
    )

    disable_syntax: Iterable[str] = dc.field(
        default_factory=list,
        metadata={
            "validator": deep_iterable(instance_of(str), instance_of((list, tuple))),
            "help": "Disable Commonmark syntax elements",
        },
    )

    all_links_external: bool = dc.field(
        default=False,
        metadata={
            "validator": instance_of(bool),
            "help": "Parse all links as simple hyperlinks",
        },
    )

    # see https://en.wikipedia.org/wiki/List_of_URI_schemes
    url_schemes: Optional[Iterable[str]] = dc.field(
        default=cast(Optional[Iterable[str]], ("http", "https", "mailto", "ftp")),
        metadata={
            "validator": optional(
                deep_iterable(instance_of(str), instance_of((list, tuple)))
            ),
            "help": "URL scheme prefixes identified as external links",
        },
    )

    ref_domains: Optional[Iterable[str]] = dc.field(
        default=None,
        metadata={
            "validator": optional(
                deep_iterable(instance_of(str), instance_of((list, tuple)))
            ),
            "help": "Sphinx domain names to search in for link references",
        },
    )

    highlight_code_blocks: bool = dc.field(
        default=True,
        metadata={
            "validator": instance_of(bool),
            "help": "Syntax highlight code blocks with pygments",
            "docutils_only": True,
        },
    )

    number_code_blocks: Sequence[str] = dc.field(
        default_factory=list,
        metadata={
            "validator": deep_iterable(instance_of(str), instance_of((list, tuple))),
            "help": "Add line numbers to code blocks with these languages",
        },
    )

    title_to_header: bool = dc.field(
        default=False,
        metadata={
            "validator": instance_of(bool),
            "help": "Convert a `title` field in the top-matter to a H1 header",
        },
    )

    heading_anchors: Optional[int] = dc.field(
        default=None,
        metadata={
            "validator": optional(in_([1, 2, 3, 4, 5, 6, 7])),
            "help": "Heading level depth to assign HTML anchors",
        },
    )

    heading_slug_func: Optional[Callable[[str], str]] = dc.field(
        default=None,
        metadata={
            "validator": optional(is_callable),
            "help": "Function for creating heading anchors",
            "global_only": True,
        },
    )

    html_meta: Dict[str, str] = dc.field(
        default_factory=dict,
        repr=False,
        metadata={
            "validator": deep_mapping(
                instance_of(str), instance_of(str), instance_of(dict)
            ),
            "merge_topmatter": True,
            "help": "HTML meta tags",
        },
    )

    footnote_transition: bool = dc.field(
        default=True,
        metadata={
            "validator": instance_of(bool),
            "help": "Place a transition before any footnotes",
        },
    )

    words_per_minute: int = dc.field(
        default=200,
        metadata={
            "validator": instance_of(int),
            "help": "For reading speed calculations",
        },
    )

    # Extension specific

    substitutions: Dict[str, Union[str, int, float]] = dc.field(
        default_factory=dict,
        repr=False,
        metadata={
            "validator": deep_mapping(
                instance_of(str), instance_of((str, int, float)), instance_of(dict)
            ),
            "merge_topmatter": True,
            "help": "Substitutions mapping",
            "extension": "substitutions",
        },
    )

    sub_delimiters: Tuple[str, str] = dc.field(
        default=("{", "}"),
        metadata={
            "validator": check_sub_delimiters,
            "help": "Substitution delimiters",
            "extension": "substitutions",
        },
    )

    linkify_fuzzy_links: bool = dc.field(
        default=True,
        metadata={
            "validator": instance_of(bool),
            "help": "Recognise URLs without schema prefixes",
            "extension": "linkify",
        },
    )

    dmath_allow_labels: bool = dc.field(
        default=True,
        metadata={
            "validator": instance_of(bool),
            "help": "Parse `$$...$$ (label)`",
            "extension": "dollarmath",
        },
    )
    dmath_allow_space: bool = dc.field(
        default=True,
        metadata={
            "validator": instance_of(bool),
            "help": "Allow initial/final spaces in `$ ... $`",
            "extension": "dollarmath",
        },
    )
    dmath_allow_digits: bool = dc.field(
        default=True,
        metadata={
            "validator": instance_of(bool),
            "help": "Allow initial/final digits `1$ ...$2`",
            "extension": "dollarmath",
        },
    )
    dmath_double_inline: bool = dc.field(
        default=False,
        metadata={
            "validator": instance_of(bool),
            "help": "Parse inline `$$ ... $$`",
            "extension": "dollarmath",
        },
    )

    update_mathjax: bool = dc.field(
        default=True,
        metadata={
            "validator": instance_of(bool),
            "help": "Update sphinx.ext.mathjax configuration to ignore `$` delimiters",
            "extension": "dollarmath",
            "global_only": True,
        },
    )

    mathjax_classes: str = dc.field(
        default="tex2jax_process|mathjax_process|math|output_area",
        metadata={
            "validator": instance_of(str),
            "help": "MathJax classes to add to math HTML",
            "extension": "dollarmath",
            "global_only": True,
        },
    )

    def __post_init__(self):
        validate_fields(self)

    def copy(self, **kwargs: Any) -> "MdParserConfig":
        """Return a new object replacing specified fields with new values.

        Note: initiating the copy will also validate the new fields.
        """
        return dc.replace(self, **kwargs)

    @classmethod
    def get_fields(cls) -> Tuple[dc.Field, ...]:
        """Return all attribute fields in this class."""
        return dc.fields(cls)

    def as_dict(self, dict_factory=dict) -> dict:
        """Return a dictionary of field name -> value."""
        return dc.asdict(self, dict_factory=dict_factory)

    def as_triple(self) -> Iterable[Tuple[str, Any, dc.Field]]:
        """Yield triples of (name, value, field)."""
        fields = {f.name: f for f in dc.fields(self.__class__)}
        for name, value in dc.asdict(self).items():
            yield name, value, fields[name]


def merge_file_level(
    config: MdParserConfig,
    topmatter: Dict[str, Any],
    warning: Callable[[str, str], None],
) -> MdParserConfig:
    """Merge the file-level topmatter with the global config.

    :param config: Global config.
    :param topmatter: Topmatter from the file.
    :param warning: Function to call with a warning (type, message).
    :returns: A new config object
    """
    # get updates
    updates: Dict[str, Any] = {}
    myst = topmatter.get("myst", {})
    if not isinstance(myst, dict):
        warning("topmatter", f"'myst' key not a dict: {type(myst)}")
    else:
        updates = myst

    # allow html_meta and substitutions at top-level for back-compatibility
    if "html_meta" in topmatter:
        warning(
            "topmatter",
            "top-level 'html_meta' key is deprecated, "
            "place under 'myst' key instead",
        )
        updates["html_meta"] = topmatter["html_meta"]
    if "substitutions" in topmatter:
        warning(
            "topmatter",
            "top-level 'substitutions' key is deprecated, "
            "place under 'myst' key instead",
        )
        updates["substitutions"] = topmatter["substitutions"]

    new = config.copy()

    # validate each update
    fields = {name: (value, field) for name, value, field in config.as_triple()}
    for name, value in updates.items():

        if name not in fields:
            warning("topmatter", f"Unknown field: {name}")
            continue

        old_value, field = fields[name]

        try:
            validate_field(new, field, value)
        except Exception as exc:
            warning("topmatter", str(exc))
            continue

        if field.metadata.get("merge_topmatter"):
            value = {**old_value, **value}

        setattr(new, name, value)

    return new


class TopmatterReadError(Exception):
    """Topmatter parsing error."""


def read_topmatter(text: Union[str, Iterator[str]]) -> Optional[Dict[str, Any]]:
    """Read the (optional) YAML topmatter from a source string.

    This is identified by the first line starting with `---`,
    then read up to a terminating line of `---`, or `...`.

    :param source: The source string to read from
    :return: The topmatter
    """
    import yaml

    if isinstance(text, str):
        if not text.startswith("---"):  # skip creating the line list in memory
            return None
        text = (line for line in text.splitlines())
    try:
        if not next(text).startswith("---"):
            return None
    except StopIteration:
        return None
    top_matter = []
    for line in text:
        if line.startswith("---") or line.startswith("..."):
            break
        top_matter.append(line.rstrip() + "\n")
    try:
        metadata = yaml.safe_load("".join(top_matter))
        assert isinstance(metadata, dict)
    except (yaml.parser.ParserError, yaml.scanner.ScannerError) as err:
        raise TopmatterReadError("Malformed YAML") from err
    if not isinstance(metadata, dict):
        raise TopmatterReadError(f"YAML is not a dict: {type(metadata)}")
    return metadata
