__version__ = "0.2.0"


def text_to_tokens(text: str):
    """Convert some text to the MyST base AST."""
    from myst_parser.block_tokens import Document
    from myst_parser.ast_renderer import AstRenderer

    # this loads the MyST specific token parsers
    with AstRenderer():
        return Document(text)


def render_tokens(root_token, renderer, **kwargs):
    """Convert a token to another format."""
    with renderer(**kwargs) as renderer:
        return renderer.render(root_token)


def setup(app):
    """Initialize Sphinx extension."""
    from myst_parser.sphinx_parser import MystParser

    app.add_source_suffix(".md", "markdown")
    app.add_source_parser(MystParser)

    return {"version": __version__, "parallel_read_safe": True}
