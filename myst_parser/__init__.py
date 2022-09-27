"""An extended commonmark compliant parser, with bridges to docutils & sphinx."""
__version__ = "0.18.1"


def setup(app):
    """Initialize the Sphinx extension."""
    from myst_parser.sphinx_ext.main import setup_sphinx

    setup_sphinx(app, load_parser=True)
    return {"version": __version__, "parallel_read_safe": True}
