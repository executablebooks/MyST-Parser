__version__ = "0.5.0a1"


def text_to_tokens(text: str):
    """Convert some text to the MyST base AST."""
    from myst_parser.block_tokens import Document
    from myst_parser.json_renderer import JsonRenderer

    # this loads the MyST specific token parsers
    with JsonRenderer():
        return Document.read(text)


def render_tokens(root_token, renderer, **kwargs):
    """Convert a token to another format."""
    with renderer(**kwargs) as renderer:
        return renderer.render(root_token)


def parse_text(text: str, output_type: str, **kwargs):
    """Convert MyST text to another format.

    :param text: the text to convert
    :param output_type: one of 'dict', 'html', 'docutils', 'sphinx'
    :param kwargs: parsed to the render initiatiation
    """
    if output_type == "dict":
        from myst_parser.ast_renderer import AstRenderer as renderer_cls
    elif output_type == "html":
        from myst_parser.html_renderer import HTMLRenderer as renderer_cls
    elif output_type == "docutils":
        from myst_parser.docutils_renderer import DocutilsRenderer as renderer_cls
    elif output_type == "sphinx":
        from myst_parser.docutils_renderer import SphinxRenderer as renderer_cls
    else:
        raise ValueError("output_type not recognised: {}".format(output_type))
    from myst_parser.block_tokens import Document

    with renderer_cls(**kwargs) as renderer:
        return renderer.render(Document.read(text))


def setup(app):
    """Initialize Sphinx extension."""
    from myst_parser.sphinx_parser import MystParser

    app.add_source_suffix(".md", "markdown")
    app.add_source_parser(MystParser)

    return {"version": __version__, "parallel_read_safe": True}
