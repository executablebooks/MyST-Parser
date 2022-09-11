"""Central handling of warnings for the myst extension."""
from __future__ import annotations

from enum import Enum
from typing import Sequence

from docutils import nodes


class MystWarnings(Enum):
    """MyST warning types."""

    CONFIG_DEPRECATED = "config"
    """A deprecated configuration option has been used."""

    RENDER_METHOD = "render"
    """The render method is not implemented."""

    MD_TOPMATTER = "topmatter"
    """Issue reading top-matter."""
    MD_DEF_DUPE = "duplicate_def"
    """Duplicate Markdown reference definition."""
    MD_FOOTNOTE_DUPE = "footnote"
    """Duplicate Markdown footnote definition."""
    MD_FOOTNOTE_MISSING = "footnote"
    """Missing Markdown footnote definition."""
    MD_HEADING_NON_CONSECUTIVE = "header"
    """Non-consecutive heading levels."""
    MD_HEADING_NESTED = "nested_header"
    """Header found nested in another element."""
    MD_INVALID_URI = "invalid_uri"
    """Link URI is not valid."""

    # cross-reference resolution
    XREF_UNSUPPORTED = "xref_unsupported"
    """Sphinx only cross-referencing."""
    XREF_TYPE = "xref_unknown_type"
    """A cross-reference was given with an unknown type."""
    XREF_MISSING = "xref_missing"
    """A target was not found for a cross-reference."""
    XREF_DUPLICATE = "xref_duplicate"
    """Multiple targets were found for a cross-reference."""
    XREF_NOT_EXPLICIT = "xref_not_explicit"
    """A target was not explicitly defined, and so may change in future."""
    XREF_EMPTY = "xref_no_content"
    """No content was resolved for a cross-reference."""
    XREF_PLACEHOLDER = "xref_replace"
    """Placeholders in a cross-reference text are missing."""
    XREF_ERROR = "xref_error"
    """An unspecified error occurred while resolving a cross-reference."""
    IREF_MISSING = "iref_missing"
    """A target was not found for an inventory reference."""
    IREF_DUPLICATE = "iref_duplicate"
    """Multiple targets were found for an inventory reference."""
    IREF_ERROR = "iref_error"
    """An unspecified error occurred while resolving an inventory reference."""
    LEGACY_DOMAIN = "domains"
    """A legacy domain found, which does not support `resolve_any_xref`."""

    # extensions
    ANCHOR_DUPE = "anchor_dupe"
    """Duplicate target anchors found."""
    STRIKETHROUGH = "strikethrough"
    """Strikethrough warning, since only implemented in HTML."""
    HTML_PARSE = "html"
    """HTML could not be parsed."""


def _is_suppressed_warning(
    type: str, subtype: str, suppress_warnings: Sequence[str]
) -> bool:
    """Check whether the warning is suppressed or not.

    Mirrors:
    https://github.com/sphinx-doc/sphinx/blob/47d9035bca9e83d6db30a0726a02dc9265bd66b1/sphinx/util/logging.py
    """
    if type is None:
        return False

    subtarget: str | None

    for warning_type in suppress_warnings:
        if "." in warning_type:
            target, subtarget = warning_type.split(".", 1)
        else:
            target, subtarget = warning_type, None

        if target == type and subtarget in (None, subtype, "*"):
            return True

    return False


def create_warning(
    document: nodes.document,
    message: str,
    subtype: MystWarnings,
    *,
    line: int | None = None,
    append_to: nodes.Element | None = None,
) -> nodes.system_message | None:
    """Generate a warning, logging if it is necessary.

    If the warning type is listed in the ``suppress_warnings`` configuration,
    then ``None`` will be returned and no warning logged.
    """
    wtype = "myst"
    # figure out whether to suppress the warning, if sphinx is available,
    # it will have been set up by the Sphinx environment,
    # otherwise we will use the configuration set by docutils
    suppress_warnings: Sequence[str] = []
    try:
        suppress_warnings = document.settings.env.app.config.suppress_warnings
    except AttributeError:
        suppress_warnings = document.settings.myst_suppress_warnings or []
    if _is_suppressed_warning(wtype, subtype.value, suppress_warnings):
        return None

    kwargs = {"line": line} if line is not None else {}
    message = f"{message} [{wtype}.{subtype.value}]"
    msg_node = document.reporter.warning(message, **kwargs)
    if append_to is not None:
        append_to.append(msg_node)
    return msg_node
