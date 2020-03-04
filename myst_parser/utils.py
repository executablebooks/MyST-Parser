from collections import namedtuple
import html
from typing import Iterable
from urllib.parse import quote


def escape_url(raw):
    """
    Escape urls to prevent code injection craziness. (Hopefully.)
    """
    return html.escape(quote(html.unescape(raw), safe="/#:()*?=%@+,&"))


TraverseResult = namedtuple("TraverseResult", ["node", "parent", "depth"])


def traverse(
    source, klass=None, depth=None, include_source=False
) -> Iterable[TraverseResult]:
    """Traverse the syntax tree, recursively yielding children.

    :param source: The source syntax element
    :param klass: filter children by a certain element class
    :param depth: The depth to recurse into the tree
    :param include_source: whether to first yield the source element

    :yield: A container for an element, its parent and depth
    """
    current_depth = 0
    if include_source:
        yield TraverseResult(source, None, current_depth)
    next_children = [(source, c) for c in getattr(source, "children", [])]
    while next_children and (depth is None or current_depth > depth):
        current_depth += 1
        new_children = []
        for parent, child in next_children:
            if klass is None or issubclass(child, klass):
                yield TraverseResult(child, parent, current_depth)
            new_children.extend([(child, c) for c in getattr(child, "children", [])])
        next_children = new_children
