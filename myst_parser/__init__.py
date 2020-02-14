__version__ = "0.1.0"


def setup(app):
    """Initialize Sphinx extension."""
    from myst_parser.sphinx_parser import MystParser, IPynbParser

    app.add_source_suffix(".md", "markdown")
    app.add_source_parser(MystParser)

    app.add_source_suffix(".ipynb", "ipynb")
    app.add_source_parser(IPynbParser)

    return {"version": __version__, "parallel_read_safe": True}
