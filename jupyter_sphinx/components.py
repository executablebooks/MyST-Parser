"""Module containing docutils/sphinx document components."""
import re

from docutils import nodes, transforms
from docutils.parsers import rst

_ANSI_RE = re.compile("\x1b\\[(.*?)([@-~])")


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
            nb_cell = env.jupyter_db.get_notebook_cell(view_node["cell_pk"])
            output_nodes = cell_output_to_nodes(
                nb_cell, env.config.jupyter_execute_data_priority, True
            )
            view_node += output_nodes


def cell_output_to_nodes(cell, data_priority, write_stderr):
    """Convert a jupyter cell with outputs and filenames to doctree nodes.
    Parameters
    ----------
    cell : jupyter cell
    data_priority : list of mime types
        Which media types to prioritize.
    write_stderr : bool
        If True include stderr in cell output

    """
    to_add = []
    for index, output in enumerate(cell.get("outputs", [])):
        output_type = output["output_type"]
        if output_type == "stream":
            if output["name"] == "stderr":
                if not write_stderr:
                    continue
                else:
                    # Output a container with an unhighlighted literal block for
                    # `stderr` messages.
                    #
                    # Adds a "stderr" class that can be customized by the user for both
                    # the container and the literal_block.
                    #
                    # Not setting "rawsource" disables Pygment hightlighting, which
                    # would otherwise add a <div class="highlight">.

                    container = nodes.container(classes=["stderr"])
                    container.append(
                        nodes.literal_block(
                            text=output["text"],
                            rawsource="",  # disables Pygment highlighting
                            language="none",
                            classes=["stderr"],
                        )
                    )
                    to_add.append(container)
            else:
                to_add.append(
                    nodes.literal_block(
                        text=output["text"],
                        rawsource=output["text"],
                        language="none",
                        classes=["output", "stream"],
                    )
                )
        elif output_type == "error":
            traceback = "\n".join(output["traceback"])
            text = _ANSI_RE.sub("", traceback)
            to_add.append(
                nodes.literal_block(
                    text=text,
                    rawsource=text,
                    language="ipythontb",
                    classes=["output", "traceback"],
                )
            )
        elif output_type in ("display_data", "execute_result"):
            try:
                # First mime_type by priority that occurs in output.
                mime_type = next(x for x in data_priority if x in output["data"])
            except StopIteration:
                continue
            data = output["data"][mime_type]
            # TODO for mime bundles that need to be saved externally,
            # it should be possible to save them by their primary key,
            # path/to/dir/jupyter_db_{pk}.{mime_extension}
            # In that way, it would also be easy to clean any no longer in use

            # if mime_type.startswith("image"):
            #     # Sphinx treats absolute paths as being rooted at the source
            #     # directory, so make a relative path, which Sphinx treats
            #     # as being relative to the current working directory.
            #     filename = os.path.basename(output.metadata["filenames"][mime_type])
            #     uri = os.path.join(dir, filename)
            #     to_add.append(nodes.image(uri=uri))
            if mime_type == "text/html":
                to_add.append(
                    nodes.raw(text=data, format="html", classes=["output", "text_html"])
                )
            elif mime_type == "text/latex":
                to_add.append(
                    nodes.raw(
                        text=data, format="latex", classes=["output", "text_latex"]
                    )
                )
            elif mime_type == "text/plain":
                to_add.append(
                    nodes.literal_block(
                        text=data,
                        rawsource=data,
                        language="none",
                        classes=["output", "text_plain"],
                    )
                )
            elif mime_type == "application/javascript":
                to_add.append(
                    nodes.raw(
                        text='<script type="{mime_type}">{data}</script>'.format(
                            mime_type=mime_type, data=data
                        ),
                        format="html",
                    )
                )
            # elif mime_type == WIDGET_VIEW_MIMETYPE:
            #     to_add.append(JupyterWidgetViewNode(view_spec=data))

    return to_add
