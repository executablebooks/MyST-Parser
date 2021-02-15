from typing import TYPE_CHECKING, List

from docutils import nodes

from .parse_html import Data, tokenize_html

if TYPE_CHECKING:
    from .docutils_renderer import DocutilsRenderer


def make_error(
    document: nodes.document, error_msg: str, text: str, line_number: int
) -> nodes.system_message:
    return document.reporter.error(
        error_msg,
        nodes.literal_block(text, text),
        line=line_number,
    )


OPTION_KEYS_IMAGE = {"class", "alt", "height", "width", "align", "name"}
# note: docutils also has scale and target

OPTION_KEYS_ADMONITION = {"class", "name"}


def default_html(text: str, source: str, line_number: int) -> List[nodes.Element]:
    raw_html = nodes.raw("", text, format="html")
    raw_html.source = source
    raw_html.line = line_number
    return [raw_html]


def html_to_nodes(
    text: str, line_number: int, renderer: "DocutilsRenderer"
) -> List[nodes.Element]:
    """Convert HTML to docutils nodes."""
    enable_html_img = "html_image" in renderer.config.get("myst_extensions", [])
    enable_html_admonition = "html_admonition" in renderer.config.get(
        "myst_extensions", []
    )

    if not (enable_html_img or enable_html_admonition):
        return default_html(text, renderer.document["source"], line_number)

    # parse the HTML to AST
    try:
        root = tokenize_html(text).strip(inplace=True, recurse=False)
    except Exception:
        msg_node = renderer.create_warning(
            "HTML could not be parsed", line=line_number, subtype="html"
        )
        return ([msg_node] if msg_node else []) + default_html(
            text, renderer.document["source"], line_number
        )

    if len(root) < 1:
        # if empty
        return default_html(text, renderer.document["source"], line_number)

    if not all(
        (enable_html_img and child.name == "img")
        or (
            enable_html_admonition
            and child.name == "div"
            and "admonition" in child.attrs.classes
        )
        for child in root
    ):
        return default_html(text, renderer.document["source"], line_number)

    nodes_list = []
    for child in root:

        if child.name == "img":
            if "src" not in child.attrs:
                return [
                    renderer.reporter.error(
                        "<img> missing 'src' attribute", line=line_number
                    )
                ]
            content = "\n".join(
                f":{k}: {v}"
                for k, v in sorted(child.attrs.items())
                if k in OPTION_KEYS_IMAGE
            )
            nodes_list.extend(
                renderer.run_directive(
                    "image", child.attrs["src"], content, line_number
                )
            )

        else:
            children = child.strip().children
            if (
                children
                and children[0].name in ("div", "p")
                and (
                    "title" in children[0].attrs.classes
                    or "admonition-title" in children[0].attrs.classes
                )
            ):
                title = "".join(child.render() for child in children.pop(0))
            else:
                title = "Note"

            options = "\n".join(
                f":{k}: {v}"
                for k, v in sorted(child.attrs.items())
                if k in OPTION_KEYS_ADMONITION
            ).rstrip()
            new_children = []
            for child in children:
                if child.name == "p":
                    new_children.extend(child.children)
                    new_children.append(Data("\n\n"))
                else:
                    new_children.append(child)
            content = (
                options
                + ("\n\n" if options else "")
                + "".join(child.render() for child in new_children).lstrip()
            )

            nodes_list.extend(
                renderer.run_directive("admonition", title, content, line_number)
            )

    return nodes_list
