__version__ = "0.12.0"


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
    from myst_parser.myst_amsmath import MystAmsMathTransform
    from myst_parser.main import MdParserConfig

    app.add_post_transform(MystReferenceResolver)
    app.add_post_transform(MystAmsMathTransform)

    for name, default in MdParserConfig().as_dict().items():
        if not name == "renderer":
            app.add_config_value(f"myst_{name}", default, "env")

    app.connect("builder-inited", create_myst_config)


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

    # https://docs.mathjax.org/en/v2.7-latest/options/preprocessors/tex2jax.html#configure-tex2jax
    if app.env.myst_config.override_mathjax:
        app.config.mathjax_config = {
            "tex2jax": {
                "inlineMath": [["\\(", "\\)"]],
                "displayMath": [["\\[", "\\]"]],
                "processRefs": False,
                "processEnvironments": False,
            }
        }
