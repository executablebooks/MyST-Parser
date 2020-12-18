from typing import TYPE_CHECKING

__version__ = "0.13.0"


if TYPE_CHECKING:
    from sphinx.application import Sphinx


def setup(app):
    """Initialize Sphinx extension."""
    from myst_parser.sphinx_parser import MystParser

    app.add_source_suffix(".md", "markdown")
    app.add_source_parser(MystParser)

    setup_sphinx(app)

    return {"version": __version__, "parallel_read_safe": True}


def setup_sphinx(app: "Sphinx"):
    """Initialize all settings and transforms in Sphinx."""
    # we do this separately to setup,
    # so that it can be called by external packages like myst_nb
    from myst_parser.myst_refs import MystReferenceResolver
    from myst_parser.mathjax import override_mathjax
    from myst_parser.main import MdParserConfig
    from myst_parser.directives import FigureMarkdown

    app.add_directive("figure-md", FigureMarkdown)

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

    # TODO remove deprecations after v0.13.0
    deprecations = {
        "myst_admonition_enable": "colon_fence",
        "myst_figure_enable": "colon_fence",
        "myst_dmath_enable": "dollarmath",
        "myst_amsmath_enable": "amsmath",
        "myst_deflist_enable": "deflist",
        "myst_html_img_enable": "html_image",
    }
    for old, new in deprecations.items():
        if app.config[old]:
            logger.warning(
                f'config `{old}` is deprecated, please add "{new}" to '
                "`myst_enable_extensions = []`"
            )
            app.config["myst_enable_extensions"].append(new)

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
