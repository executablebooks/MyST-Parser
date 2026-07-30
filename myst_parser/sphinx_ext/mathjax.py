"""Overrides to ``sphinx.ext.mathjax``

This fixes two issues:

1. Mathjax should not search for ``$`` delimiters, nor LaTeX amsmath environments,
   since we already achieve this with the dollarmath and amsmath markdown-it-py plugins
2. amsmath math blocks should be wrapped in mathjax delimiters (default ``\\[...\\]``),
   and assigned an equation number

"""

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.ext import mathjax
from sphinx.locale import _
from sphinx.util import logging
from sphinx.util.math import get_node_equation_number
from sphinx.writers.html import HTMLTranslator

logger = logging.getLogger(__name__)


def log_override_warning(app: Sphinx, config_name: str, current: str, new: str) -> None:
    """Log a warning if MathJax configuration being overridden."""
    if logging.is_suppressed_warning("myst", "mathjax", app.config.suppress_warnings):
        return
    logger.warning(
        f"`{config_name}['options']['processHtmlClass']` "
        f"is being overridden by myst-parser: '{current}' -> '{new}'. "
        "Set `suppress_warnings=['myst.mathjax']` to ignore this warning, or "
        "`myst_update_mathjax=False` if this is undesirable."
    )


def override_mathjax(app: Sphinx):
    """Override aspects of the mathjax extension.

    MyST-Parser parses dollar and latex math, via markdown-it plugins.
    Therefore, we tell Mathjax to only render these HTML elements.
    This is accompanied by setting the `ignoreClass` on the top-level section of each MyST document.
    """
    if (
        "amsmath" in app.config["myst_enable_extensions"]
        and "mathjax" in app.registry.html_block_math_renderers
    ):
        app.registry.html_block_math_renderers["mathjax"] = (
            html_visit_displaymath,
            None,
        )

    if "dollarmath" not in app.config["myst_enable_extensions"]:
        return
    if not app.env.myst_config.update_mathjax:  # type: ignore[attr-defined]
        return

    mjax_classes = app.env.myst_config.mathjax_classes  # type: ignore[attr-defined]

    # Determine which mathjax config to modify:
    # prefer whichever the user has explicitly set, falling back to
    # the Sphinx version's default (mathjax4_config for Sphinx 9+, mathjax3_config for 8).
    # Note: if a user sets both mathjax3_config and mathjax4_config, we only update
    # the v4 config (Sphinx emits both but v4 clobbers v3 at runtime anyway).
    has_mjax4 = hasattr(app.config, "mathjax4_config")
    if has_mjax4 and app.config.mathjax4_config:
        config_attr = "mathjax4_config"
    elif app.config.mathjax3_config:
        config_attr = "mathjax3_config"
    elif has_mjax4:
        config_attr = "mathjax4_config"
    else:
        config_attr = "mathjax3_config"

    config: dict = getattr(app.config, config_attr) or {}  # type: ignore[type-arg]
    config.setdefault("options", {})
    if (
        "processHtmlClass" in config["options"]
        and config["options"]["processHtmlClass"] != mjax_classes
    ):
        log_override_warning(
            app,
            config_attr,
            config["options"]["processHtmlClass"],
            mjax_classes,
        )
    config["options"]["processHtmlClass"] = mjax_classes
    setattr(app.config, config_attr, config)


def html_visit_displaymath(self: HTMLTranslator, node: nodes.math_block) -> None:
    """Override for sphinx.ext.mathjax.html_visit_displaymath to handle amsmath.

    By default displaymath, are normally wrapped in a prefix/suffix,
    defined by mathjax_display, and labelled nodes are numbered.
    However, this is not the case if the math_block is set as 'nowrap', as for amsmath.
    Therefore, we need to override this behaviour.
    """
    if "amsmath" in node.get("classes", []):
        self.body.append(
            self.starttag(node, "div", CLASS="math notranslate nohighlight amsmath")
        )
        if node["number"]:
            number = get_node_equation_number(self, node)
            self.body.append(f'<span class="eqno">({number})')
            self.add_permalink_ref(node, _("Permalink to this equation"))
            self.body.append("</span>")
        prefix, suffix = self.builder.config.mathjax_display
        self.body.append(prefix)
        self.body.append(self.encode(node.astext()))
        self.body.append(suffix)
        self.body.append("</div>\n")
        raise nodes.SkipNode

    return mathjax.html_visit_displaymath(self, node)
