"""Module containing docutils/sphinx document components."""
import os
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
        doc_relpath = os.path.dirname(env.docname)  # relative to src dir
        output_dir = os.path.join(output_directory(env), doc_relpath)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        for exec_node in self.document.traverse(JupyterExecNode):
            # add language lexer
            language = env.jupyter_db.get_cell_language(exec_node["cell_pk"])
            exec_node.children[0].attributes["language"] = language
        for view_node in self.document.traverse(JupyterViewNode):
            output_nodes, images = cell_output_to_nodes(
                env.jupyter_db,
                view_node["cell_pk"],
                env.config.jupyter_execute_data_priority,
                True,
            )
            view_node += output_nodes
            # handle creating image uri's
            # dir_path = sphinx_abs_dir(env)
            for mime_pk, image_nodes in images.items():
                uri = env.jupyter_db.write_mime_to_file(mime_pk, output_dir)
                for image_node in image_nodes:
                    image_node["uri"] = uri
                    image_node["candidates"] = {"?": uri}

            # TODO remove images that are no longer used


# Note: for images and downloadable files
# since we are adding them at the post transform stage,
# they will not be processed by environment collectors, that trigger just after parsing.
# https://www.sphinx-doc.org/en/master/extdev/collectorapi.html#module-sphinx.environment.collectors
# sphinx.environment.collectors.asset.ImageCollector
# sphinx.environment.collectors.asset.DownloadFileCollector


def cell_output_to_nodes(db, pk, data_priority, write_stderr):
    """Convert a jupyter cell with outputs and filenames to doctree nodes.
    Parameters
    ----------
    cell : jupyter cell
    data_priority : list of mime types
        Which media types to prioritize.
    write_stderr : bool
        If True include stderr in cell output

    """
    node_list = []
    images = {}
    for output in db.iter_outputs(pk):
        if output.output_type == "stream":
            node_list.extend(stream_output_to_nodes(output, write_stderr))
        elif output.output_type == "error":
            traceback = "\n".join(output.traceback)
            text = _ANSI_RE.sub("", traceback)
            node_list.append(
                nodes.literal_block(
                    text=text,
                    rawsource=text,
                    language="ipythontb",
                    classes=["output", "traceback"],
                )
            )
        elif output.output_type in ("display_data", "execute_result"):
            node_list.extend(data_output_to_nodes(output, data_priority, images))
    return node_list, images


def stream_output_to_nodes(output, write_stderr):
    node_list = []
    if output.name == "stderr":
        if not write_stderr:
            return []
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
                    text=output.text,
                    rawsource="",  # disables Pygment highlighting
                    language="none",
                    classes=["stderr"],
                )
            )
            node_list.append(container)
    else:
        node_list.append(
            nodes.literal_block(
                text=output.text,
                rawsource=output.text,
                language="none",
                classes=["output", "stream"],
            )
        )
    return node_list


def data_output_to_nodes(output, data_priority, images):
    node_list = []
    try:
        # First mime_type by priority that occurs in output.
        mime_type = next(x for x in data_priority if x in output.data)
    except StopIteration:
        return []
    data = output.data[mime_type]

    if mime_type.startswith("image"):
        image = nodes.image()
        images.setdefault(data.pk, []).append(image)
        node_list.append(image)

    if mime_type == "text/html":
        node_list.append(
            nodes.raw(text=str(data), format="html", classes=["output", "text_html"])
        )
    elif mime_type == "text/latex":
        node_list.append(
            nodes.raw(text=str(data), format="latex", classes=["output", "text_latex"])
        )
    elif mime_type == "text/plain":
        node_list.append(
            nodes.literal_block(
                text=str(data),
                rawsource=str(data),
                language="none",
                classes=["output", "text_plain"],
            )
        )
    elif mime_type == "application/javascript":
        node_list.append(
            nodes.raw(
                text='<script type="{mime_type}">{data}</script>'.format(
                    mime_type=mime_type, data=str(data)
                ),
                format="html",
            )
        )
    # elif mime_type == WIDGET_VIEW_MIMETYPE:
    #     node_list.append(JupyterWidgetViewNode(view_spec=str(data)))
    return node_list


def output_directory(env):
    # Put output images inside the sphinx build directory to avoid
    # polluting the current working directory. We don't use a
    # temporary directory, as sphinx may cache the doctree with
    # references to the images that we write

    # Note: we are using an implicit fact that sphinx output directories are
    # direct subfolders of the build directory.
    return os.path.abspath(
        os.path.join(env.app.outdir, os.path.pardir, "jupyter_execute")
    )


def sphinx_abs_dir(env):
    # We write the output files into
    # output_directory / jupyter_execute / path relative to source directory
    # Sphinx expects download links relative to source file or relative to
    # source dir and prepended with '/'. We use the latter option.
    return "/" + os.path.relpath(
        os.path.abspath(
            os.path.join(output_directory(env), os.path.dirname(env.docname))
        ),
        os.path.abspath(env.app.srcdir),
    )
