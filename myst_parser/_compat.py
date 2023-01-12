"""Helpers for cross compatibility across dependency versions."""
import sys
from typing import Callable, Iterable

from docutils.nodes import Element

if sys.version_info >= (3, 8):
    from typing import Literal, Protocol, TypedDict, get_args, get_origin
else:
    from typing_extensions import (  # noqa: F401
        Literal,
        Protocol,
        TypedDict,
        get_args,
        get_origin,
    )


def findall(node: Element) -> Callable[..., Iterable[Element]]:
    """Iterate through"""
    # findall replaces traverse in docutils v0.18
    # note a difference is that findall is an iterator
    return getattr(node, "findall", node.traverse)
