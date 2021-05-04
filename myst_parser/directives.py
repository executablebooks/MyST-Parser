"""MyST specific directives"""
from typing import List, Tuple

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.directives import SphinxDirective
from sphinx.util.docutils import SphinxRole


def align(argument):
    return directives.choice(argument, ("left", "center", "right"))


def figwidth_value(argument):
    if argument.lower() == "image":
        return "image"
    else:
        return directives.length_or_percentage_or_unitless(argument, "px")


class SubstitutionReferenceRole(SphinxRole):
    """Implement substitution references as a role.

    Note, in ``docutils/parsers/rst/roles.py`` this is left unimplemented.
    """

    def run(self) -> Tuple[List[nodes.Node], List[nodes.system_message]]:
        subref_node = nodes.substitution_reference(self.rawtext, self.text)
        self.set_source_info(subref_node, self.lineno)  # type: ignore[arg-type]
        subref_node["refname"] = nodes.fully_normalize_name(self.text)
        return [subref_node], []


class FigureMarkdown(SphinxDirective):
    """Directive for creating a figure with Markdown compatible syntax.

    Example::

        :::{figure-md} target
        <img src="img/fun-fish.png" alt="fishy" class="bg-primary mb-1" width="200px">

        This is a caption in **Markdown**
        :::

    """

    required_arguments = 0
    optional_arguments = 1  # image target
    final_argument_whitespace = True
    has_content = True

    option_spec = {
        "width": figwidth_value,
        "class": directives.class_option,
        "align": align,
        "name": directives.unchanged,
    }

    def run(self) -> List[nodes.Node]:
        figwidth = self.options.pop("width", None)
        figclasses = self.options.pop("class", None)
        align = self.options.pop("align", None)

        # parser = default_parser(self.env.myst_config)

        node = nodes.Element()
        # TODO test that we are using myst parser
        # ensure html image enabled
        myst_extensions = self.state._renderer.config.get("myst_extensions", set())
        try:
            self.state._renderer.config.setdefault("myst_extensions", set())
            self.state._renderer.config["myst_extensions"].add("html_image")
            self.state.nested_parse(self.content, self.content_offset, node)
        finally:
            self.state._renderer.config["myst_extensions"] = myst_extensions

        if not len(node.children) == 2:
            return [
                self.figure_error(
                    "content should be one image, "
                    "followed by a single paragraph caption"
                )
            ]

        image_node, caption_para = node.children
        if isinstance(image_node, nodes.paragraph):
            image_node = image_node[0]

        if not isinstance(image_node, nodes.image):
            return [
                self.figure_error(
                    "content should be one image (not found), "
                    "followed by single paragraph caption"
                )
            ]

        if not isinstance(caption_para, nodes.paragraph):
            return [
                self.figure_error(
                    "content should be one image, "
                    "followed by single paragraph caption (not found)"
                )
            ]

        caption_node = nodes.caption(caption_para.rawsource, "", *caption_para.children)
        caption_node.source = caption_para.source
        caption_node.line = caption_para.line

        figure_node = nodes.figure("", image_node, caption_node)
        self.set_source_info(figure_node)

        if figwidth is not None:
            figure_node["width"] = figwidth
        if figclasses:
            figure_node["classes"] += figclasses
        if align:
            figure_node["align"] = align
        if self.arguments:
            self.options["name"] = self.arguments[0]
            self.add_name(figure_node)

        return [figure_node]

    def figure_error(self, message):
        """A warning for reporting an invalid figure."""
        error = self.state_machine.reporter.error(
            message,
            nodes.literal_block(self.block_text, self.block_text),
            line=self.lineno,
        )
        return error
