"""Overrides to ``sphinx.ext.mathjax``

This fixes two issues:

1. Mathjax should not search for ``$`` delimiters, nor LaTeX amsmath environments,
   since we already achieve this with the dollarmath and amsmath mrakdown-it-py plugins
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


def override_mathjax(app: Sphinx):
    """Override aspects of the mathjax extension, but only if necessary."""

    if (
        app.config["myst_amsmath_enable"]
        and "mathjax" in app.registry.html_block_math_renderers
    ):
        app.registry.html_block_math_renderers["mathjax"] = (
            html_visit_displaymath,
            None,
        )
    # https://docs.mathjax.org/en/v2.7-latest/options/preprocessors/tex2jax.html#configure-tex2jax
    if app.config.mathjax_config is None and app.env.myst_config.update_mathjax:
        app.config.mathjax_config = {
            "tex2jax": {
                "inlineMath": [["\\(", "\\)"]],
                "displayMath": [["\\[", "\\]"]],
                "processRefs": False,
                "processEnvironments": False,
            }
        }
    elif app.env.myst_config.update_mathjax:
        if "tex2jax" in app.config.mathjax_config:
            logger.warning(
                "`mathjax_config['tex2jax']` is set, but `myst_update_mathjax = True`, "
                "and so this will be overridden. "
                "Set `myst_update_mathjax = False` if you wish to use your own config"
            )
        app.config.mathjax_config["tex2jax"] = {
            "inlineMath": [["\\(", "\\)"]],
            "displayMath": [["\\[", "\\]"]],
            "processRefs": False,
            "processEnvironments": False,
        }


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
            self.body.append('<span class="eqno">(%s)' % number)
            self.add_permalink_ref(node, _("Permalink to this equation"))
            self.body.append("</span>")
        prefix, suffix = self.builder.config.mathjax_display
        self.body.append(prefix)
        self.body.append(self.encode(node.astext()))
        self.body.append(suffix)
        self.body.append("</div>\n")
        raise nodes.SkipNode

    return mathjax.html_visit_displaymath(self, node)
