"""Module containing docutils/sphinx document components."""
from docutils import nodes, transforms
from docutils.parsers import rst


class JupyterKernel(rst.Directive):
    required_arguments = 1  # kernel type
    optional_arguments = 0
    final_argument_whitespace = False
    has_content = False
    option_spec = {
        "name": rst.directives.unchanged_required,
        "allow_errors": rst.directives.flag
        # TODO add other specs, e.g. timeouts
    }

    def run(self):
        env = self.state.document.settings.env
        name = self.arguments[0]
        try:
            env.jupyter_db.get_or_create_kernel(
                doc_uri=env.docname,
                kernel_type=name,
                name=self.options.get("name", None),
                metadata={"allow_errors": "allow_errors" in self.options},
            )
        except Exception as err:
            raise self.error(f"Code kernel: {err}")

        return []


class JupyterExecNode(nodes.Element):
    pass


class JupyterExec(rst.Directive):
    required_arguments = 0
    optional_arguments = 1  # language
    final_argument_whitespace = False
    has_content = True
    option_spec = {
        "name": rst.directives.unchanged,
        "kernel": rst.directives.unchanged,
        "timeout": rst.directives.positive_int,
        "show-code": rst.directives.flag,
        "label": rst.directives.unchanged,
    }

    def run(self):
        env = self.state.document.settings.env
        language = self.arguments[0] if self.arguments else None
        source = "\n".join(self.content.data)

        try:
            # TODO can we record the line number in the source text
            # in order to use when reporting execution errors later.
            cell = env.jupyter_db.add_code_cell(
                source,
                env.docname,
                name=self.options.get("name", None),
                kernel_name=self.options.get("kernel", None),
                metadata={"timeout": self.options.get("timeout", None)},
            )
        except Exception as err:
            raise self.error(f"Code cell: {err}")

        if "show-code" in self.options:
            # Note we do not yet necessarily know the language of the code yet
            # so this must be added/checked in a post-transform
            # TODO add target node for label
            literal_node = nodes.literal_block(
                rawsource=source, text=source, language=language
            )
            containing_node = JupyterExecNode("", literal_node, cell_pk=cell.pk)
            return [containing_node]
        return []


class JupyterViewNode(nodes.Element):
    pass


class JupyterView(rst.Directive):
    required_arguments = 0
    optional_arguments = 1  # code cell name
    final_argument_whitespace = False
    has_content = True
    option_spec = {
        "index": rst.directives.nonnegative_int,
        "mimetype": rst.directives.unchanged,
        "render_type": rst.directives.unchanged,
        "label": rst.directives.unchanged,
    }

    def run(self):
        env = self.state.document.settings.env
        inner_nodes = []
        if self.content:
            caption_node = nodes.caption()
            self.state.nested_parse(self.content, self.content_offset, caption_node)
            # TODO assert only one paragraph?
            inner_nodes.append(caption_node)

        name = None
        if self.arguments:
            name = self.arguments[0]

        try:
            code_cell = env.jupyter_db.get_code_cell(env.docname, name=name)
        except Exception as err:
            raise self.error(f"Code view: {err}")

        # TODO add target node for label
        containing_node = JupyterViewNode(
            "",
            *inner_nodes,
            cell_pk=code_cell.pk,
            output_index=self.options.get("index", None),
            mimetype=self.options.get("mimetype", None),
            render_type=self.options.get("render_type", None),
        )
        return [containing_node]


class ResolveJupyterViews(transforms.Transform):
    default_priority = 100  # TODO default_priority?

    def apply(self):
        env = self.document.settings.env
        for exec_node in self.document.traverse(JupyterExecNode):
            # add language lexer
            language = env.jupyter_db.get_cell_language(exec_node["cell_pk"])
            exec_node.children[0].attributes["language"] = language
        for view_node in self.document.traverse(JupyterViewNode):
            # TODO add output
            view_node["cell_pk"]
