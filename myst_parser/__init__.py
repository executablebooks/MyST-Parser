__version__ = "0.10.0"


def setup(app):
    """Initialize Sphinx extension."""
    from myst_parser.sphinx_parser import MystParser
    from myst_parser.myst_refs import MystReferenceResolver

    app.add_source_suffix(".md", "markdown")
    app.add_source_parser(MystParser)
    app.add_config_value("myst_config", {}, "env")
    app.add_post_transform(MystReferenceResolver)

    return {"version": __version__, "parallel_read_safe": True}
