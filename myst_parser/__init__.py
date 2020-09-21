__version__ = "0.12.10"


def setup(app):
    """Initialize Sphinx extension."""
    from myst_parser.sphinx_parser import MystParser

    app.add_source_suffix(".md", "markdown")
    app.add_source_parser(MystParser)

    setup_sphinx(app)

    return {"version": __version__, "parallel_read_safe": True}


def setup_sphinx(app):
    """Initialize all settings and transforms in Sphinx."""
    # we do this separately to setup,
    # so that it can be called by external packages like myst_nb
    from myst_parser.myst_refs import MystReferenceResolver
    from myst_parser.mathjax import override_mathjax
    from myst_parser.main import MdParserConfig

    app.add_post_transform(MystReferenceResolver)

    for name, default in MdParserConfig().as_dict().items():
        if not name == "renderer":
            app.add_config_value(f"myst_{name}", default, "env")

    app.connect("builder-inited", create_myst_config)
    app.connect("builder-inited", override_mathjax)


def create_myst_config(app):
    from sphinx.util import logging
    from sphinx.util.console import bold
    from myst_parser.main import MdParserConfig

    logger = logging.getLogger(__name__)

    values = {
        name: app.config[f"myst_{name}"]
        for name in MdParserConfig().as_dict().keys()
        if name != "renderer"
    }

    try:
        app.env.myst_config = MdParserConfig(**values)
        logger.info(bold("myst v%s:") + " %s", __version__, app.env.myst_config)
    except (TypeError, ValueError) as error:
        logger.error("myst configuration invalid: %s", error.args[0])
        app.env.myst_config = MdParserConfig()
