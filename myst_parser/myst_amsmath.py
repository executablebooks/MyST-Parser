from typing import Any

from docutils import nodes

from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.util.nodes import NodeMatcher


class MystAmsMathTransform(SphinxPostTransform):
    """For the default mathjax renderer,
    math_blocks are normally wrapped in a prefix/suffix defined by mathjax_display
    However, this is not the case if the math_block is set as nowrap,
    as set for amsmath.
    Therefore, we need to do this independently.
    """

    default_priority = 400
    builders = ("html",)

    def run(self, **kwargs: Any) -> None:
        matcher = NodeMatcher(nodes.math_block, classes=["amsmath"])
        for node in self.document.traverse(matcher):  # type: nodes.math_block
            prefix, suffix = self.config.myst_amsmath_html
            node.children[0] = nodes.Text(prefix + str(node.children[0]) + suffix)
