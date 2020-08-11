from typing import Any

from docutils import nodes

from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.util.nodes import NodeMatcher


class MystAmsMathTransform(SphinxPostTransform):
    """For the default mathjax renderer,
    math_blocks are normally wrapped in a prefix/suffix defined by mathjax_display,
    and labeled nodes are numbered.
    However, this is not the case if the math_block is set as nowrap,
    as set for amsmath.
    Therefore, we need to do this independently.
    """

    default_priority = 400

    def run(self, **kwargs: Any) -> None:
        if "html" not in self.app.builder.name and self.app.builder.name not in (
            "readthedocs",
        ):
            return
        if self.app.builder.math_renderer_name != "mathjax":
            return
        matcher = NodeMatcher(nodes.math_block, classes=["amsmath"])
        for node in self.document.traverse(matcher):  # type: nodes.math_block
            prefix, suffix = self.config.mathjax_display
            node.children[0] = nodes.Text(prefix + str(node.children[0]) + suffix)
            replace = []
            if node["number"]:
                number = get_node_equation_number(self, node)
                replace.append(
                    nodes.raw(
                        "", f'<span class="eqno">({number})</span>', format="html"
                    )
                )
            # TODO add permalink (see sphinx/ext/mathjax.py)
            # self.add_permalink_ref(node, _('Permalink to this equation'))
            replace.append(node)
            node.replace_self(replace)


def get_node_equation_number(tr: SphinxPostTransform, node: nodes.math_block) -> str:
    """Adapted from sphinx/util/math.py"""
    if tr.config.math_numfig and tr.config.numfig:
        figtype = "displaymath"
        if tr.app.builder.name == "singlehtml":
            # TODO is this the right docname?
            key = "%s/%s" % (tr.app.env.docname, figtype)
        else:
            key = figtype

        id = node["ids"][0]
        number = tr.app.builder.fignumbers.get(key, {}).get(id, ())
        return ".".join(map(str, number))
    else:
        return node["number"]
