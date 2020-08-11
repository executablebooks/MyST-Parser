__version__ = "0.10.0"


def setup(app):
    """Initialize Sphinx extension."""
    from myst_parser.sphinx_parser import MystParser
    from myst_parser.myst_refs import MystReferenceResolver
    from myst_parser.myst_amsmath import MystAmsMathTransform

    app.add_source_suffix(".md", "markdown")
    app.add_source_parser(MystParser)
    app.add_post_transform(MystReferenceResolver)
    app.add_post_transform(MystAmsMathTransform)

    app.add_config_value("myst_math_delimiters", "dollars", "env")
    app.add_config_value("myst_disable_syntax", (), "env")
    app.add_config_value("myst_amsmath_enable", False, "env")
    app.add_config_value("myst_amsmath_html", [r"\[", r"\]"], "html")

    app.connect("config-inited", validate_config)

    return {"version": __version__, "parallel_read_safe": True}


def validate_config(app, config):
    from sphinx.util import logging

    logger = logging.getLogger(__name__)

    # TODO raise errors or log error with sphinx?
    try:
        for s in config.myst_disable_syntax:
            assert isinstance(s, str)
    except (AssertionError, TypeError):
        logger.error("myst_disable_syntax config option not of type List[str]")

    allowed_delimiters = ["brackets", "kramdown", "dollars", "julia"]
    if config.myst_math_delimiters not in allowed_delimiters:
        logger.error(
            "myst_math_delimiters config option not an allowed name: "
            + f"{allowed_delimiters}"
        )

    if not isinstance(config.myst_amsmath_enable, bool):
        logger.error("myst_disable_syntax config option not of type boolean")
