"""The setup for the sphinx extension."""
from typing import Any, Dict

from sphinx.application import Sphinx

from myst_parser.warnings import MystWarnings

DEPRECATED = "__deprecated__"


def setup_sphinx(app: Sphinx, load_parser=False):
    """Initialize all settings and transforms in Sphinx."""
    # we do this separately to setup,
    # so that it can be called by external packages like myst_nb
    from myst_parser.config.main import MdParserConfig
    from myst_parser.parsers.sphinx_ import MystParser
    from myst_parser.sphinx_ext.directives import (
        FigureMarkdown,
        SubstitutionReferenceRole,
    )
    from myst_parser.sphinx_ext.mathjax import override_mathjax
    from myst_parser.sphinx_ext.references import (
        MystDomain,
        MystReferencesBuilder,
        MystRefrenceResolver,
    )

    if load_parser:
        app.add_source_suffix(".md", "markdown")
        app.add_source_parser(MystParser)

    app.add_role("sub-ref", SubstitutionReferenceRole())
    app.add_directive("figure-md", FigureMarkdown)

    app.add_domain(MystDomain)
    app.add_post_transform(MystRefrenceResolver)
    app.add_builder(MystReferencesBuilder)

    for name, default, field in MdParserConfig().as_triple():
        if not field.metadata.get("docutils_only", False):
            # TODO add types?
            if field.metadata.get("deprecated"):
                app.add_config_value(f"myst_{name}", DEPRECATED, "env", types=Any)
            else:
                app.add_config_value(f"myst_{name}", default, "env", types=Any)

    app.connect("builder-inited", create_myst_config)
    app.connect("builder-inited", override_mathjax)


def create_myst_config(app):
    from sphinx.util import logging

    # Ignore type checkers because the attribute is dynamically assigned
    from sphinx.util.console import bold  # type: ignore[attr-defined]

    from myst_parser import __version__
    from myst_parser.config.main import MdParserConfig

    logger = logging.getLogger(__name__)

    values: Dict[str, Any] = {}

    for name, _, field in MdParserConfig().as_triple():
        if not field.metadata.get("docutils_only", False):
            if field.metadata.get("deprecated"):
                if app.config[f"myst_{name}"] != DEPRECATED:
                    logger.warning(
                        f"'myst_{name}' is deprecated, "
                        f"{field.metadata.get('deprecated')} [myst.config]",
                        type="myst",
                        subtype=MystWarnings.CONFIG_DEPRECATED.value,
                    )
                continue
            values[name] = app.config[f"myst_{name}"]

    try:
        app.env.myst_config = MdParserConfig(**values)
        logger.info(bold("myst v%s:") + " %s", __version__, app.env.myst_config)
    except (TypeError, ValueError) as error:
        logger.error("myst configuration invalid: %s", error.args[0])
        app.env.myst_config = MdParserConfig()
