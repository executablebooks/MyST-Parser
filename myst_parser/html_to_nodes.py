from typing import List, Optional

from docutils import nodes
from docutils.parsers.rst import directives

from .parse_html import tokenize_html


def align(argument: str) -> str:
    return directives.choice(argument, ("left", "center", "right"))


def make_error(
    document: nodes.document, error_msg: str, text: str, line_number: int
) -> nodes.system_message:
    return document.reporter.error(
        "<img> conversion: {}".format(error_msg),
        nodes.literal_block(text, text),
        line=line_number,
    )


def html_to_nodes(
    text: str, document: nodes.document, line_number: int
) -> Optional[List[nodes.Element]]:
    root = tokenize_html(text).strip(inplace=True, recurse=False)
    if len(root) < 1:
        return None
    if not all(child.name == "img" for child in root):
        return None

    nodes_list = []
    for child in root:
        if "src" not in child.attrs:
            return [make_error(document, "missing src attribute", text, line_number)]
        options = {}
        for name, key, spec in [
            ("src", "uri", directives.uri),
            ("class", "classes", directives.class_option),
            ("alt", "alt", directives.unchanged),
            ("height", "height", directives.length_or_unitless),
            ("width", "width", directives.length_or_percentage_or_unitless),
            ("align", "align", align)
            # note: docutils also has scale and target
        ]:
            if name in child.attrs:
                value = child.attrs[name]
                try:
                    options[key] = spec(value)
                except (ValueError, TypeError) as error:
                    error_msg = "Invalid attribute: (key: '{}'; value: {})\n{}".format(
                        name, value, error
                    )
                    return [make_error(document, error_msg, text, line_number)]

        node = nodes.image(text, **options)
        if "name" in child.attrs:
            name = nodes.fully_normalize_name(child.attrs["name"])
            node["names"].append(name)
            document.note_explicit_target(node, node)
        nodes_list.append(node)

    return nodes_list
