import os
import docutils
from sphinx import parsers
from docutils import frontend
from docutils.nodes import container, literal_block
import nbformat as nbf
from jupyter_sphinx.execute import (
    write_notebook_output,
    cell_output_to_nodes,
    sphinx_abs_dir,
    output_directory,
    JupyterWidgetStateNode,
    JupyterWidgetViewNode
)

from myst_parser.docutils_renderer import SphinxRenderer
from myst_parser.block_tokens import Document


class MystParser(parsers.Parser):
    """Docutils parser for CommonMark + Math + Tables + RST Extensions """

    supported = ("md", "markdown")
    translate_section_name = None

    default_config = {"known_url_schemes": None}

    # these specs are copied verbatim from the docutils RST parser
    settings_spec = (
        "Myst Parser Options",
        None,
        (
            (
                'Recognize and link to standalone PEP references (like "PEP 258").',
                ["--pep-references"],
                {"action": "store_true", "validator": frontend.validate_boolean},
            ),
            (
                "Base URL for PEP references "
                '(default "http://www.python.org/dev/peps/").',
                ["--pep-base-url"],
                {
                    "metavar": "<URL>",
                    "default": "http://www.python.org/dev/peps/",
                    "validator": frontend.validate_url_trailing_slash,
                },
            ),
            (
                'Template for PEP file part of URL. (default "pep-%04d")',
                ["--pep-file-url-template"],
                {"metavar": "<URL>", "default": "pep-%04d"},
            ),
            (
                'Recognize and link to standalone RFC references (like "RFC 822").',
                ["--rfc-references"],
                {"action": "store_true", "validator": frontend.validate_boolean},
            ),
            (
                'Base URL for RFC references (default "http://tools.ietf.org/html/").',
                ["--rfc-base-url"],
                {
                    "metavar": "<URL>",
                    "default": "http://tools.ietf.org/html/",
                    "validator": frontend.validate_url_trailing_slash,
                },
            ),
            (
                "Set number of spaces for tab expansion (default 8).",
                ["--tab-width"],
                {
                    "metavar": "<width>",
                    "type": "int",
                    "default": 8,
                    "validator": frontend.validate_nonnegative_int,
                },
            ),
            (
                "Remove spaces before footnote references.",
                ["--trim-footnote-reference-space"],
                {"action": "store_true", "validator": frontend.validate_boolean},
            ),
            (
                "Leave spaces before footnote references.",
                ["--leave-footnote-reference-space"],
                {"action": "store_false", "dest": "trim_footnote_reference_space"},
            ),
            (
                "Disable directives that insert the contents of external file "
                '("include" & "raw"); replaced with a "warning" system message.',
                ["--no-file-insertion"],
                {
                    "action": "store_false",
                    "default": 1,
                    "dest": "file_insertion_enabled",
                    "validator": frontend.validate_boolean,
                },
            ),
            (
                "Enable directives that insert the contents of external file "
                '("include" & "raw").  Enabled by default.',
                ["--file-insertion-enabled"],
                {"action": "store_true"},
            ),
            (
                'Disable the "raw" directives; replaced with a "warning" '
                "system message.",
                ["--no-raw"],
                {
                    "action": "store_false",
                    "default": 1,
                    "dest": "raw_enabled",
                    "validator": frontend.validate_boolean,
                },
            ),
            (
                'Enable the "raw" directive.  Enabled by default.',
                ["--raw-enabled"],
                {"action": "store_true"},
            ),
            (
                "Token name set for parsing code with Pygments: one of "
                '"long", "short", or "none (no parsing)". Default is "long".',
                ["--syntax-highlight"],
                {
                    "choices": ["long", "short", "none"],
                    "default": "long",
                    "metavar": "<format>",
                },
            ),
            (
                "Change straight quotation marks to typographic form: "
                'one of "yes", "no", "alt[ernative]" (default "no").',
                ["--smart-quotes"],
                {
                    "default": False,
                    "metavar": "<yes/no/alt>",
                    "validator": frontend.validate_ternary,
                },
            ),
            (
                'Characters to use as "smart quotes" for <language>. ',
                ["--smartquotes-locales"],
                {
                    "metavar": "<language:quotes[,language:quotes,...]>",
                    "action": "append",
                    "validator": frontend.validate_smartquotes_locales,
                },
            ),
            (
                "Inline markup recognized at word boundaries only "
                "(adjacent to punctuation or whitespace). "
                "Force character-level inline markup recognition with "
                '"\\ " (backslash + space). Default.',
                ["--word-level-inline-markup"],
                {"action": "store_false", "dest": "character_level_inline_markup"},
            ),
            (
                "Inline markup recognized anywhere, regardless of surrounding "
                "characters. Backslash-escapes must be used to avoid unwanted "
                "markup recognition. Useful for East Asian languages. "
                "Experimental.",
                ["--character-level-inline-markup"],
                {
                    "action": "store_true",
                    "default": False,
                    "dest": "character_level_inline_markup",
                },
            ),
        ),
    )

    config_section = "myst parser"
    config_section_dependencies = ("parsers",)

    def parse(self, inputstring, document):
        # TODO add conf.py configurable settings
        self.config = self.default_config.copy()
        try:
            new_cfg = self.document.settings.env.config.myst_config
            self.config.update(new_cfg)
        except AttributeError:
            pass
        renderer = SphinxRenderer(document=document)
        with renderer:
            renderer.render(Document(inputstring))


class IPynbParser(MystParser):
    """Docutils parser for IPynb + CommonMark + Math + Tables + RST Extensions """

    supported = ("ipynb",)
    translate_section_name = None

    default_config = {"known_url_schemes": None}

    config_section = "ipynb parser"
    config_section_dependencies = ("parsers",)

    def parse(self, inputstring, document):
        self.config = self.default_config.copy()
        try:
            new_cfg = self.document.settings.env.config.myst_config
            self.config.update(new_cfg)
        except AttributeError:
            pass

        ntbk = nbf.reads(inputstring, nbf.NO_CONVERT)
        filename = document.attributes["source"]
        notebook_name = os.path.basename(filename).strip(".ipynb")
        for cell in ntbk.cells:
            # Cell container will wrap whatever is in the cell
            sphinx_cell = container(classes=["cell"], cell_type=cell["cell_type"])
            # Give *all* cells an input container just to make it more consistent
            cell_input = container(classes=["cell_input"])
            sphinx_cell += cell_input
            document += sphinx_cell

            # If a markdown cell, simply call the Myst parser and append children
            if cell["cell_type"] == "markdown":
                # Initialize the render so that it'll append things to our current cell
                renderer = SphinxRenderer(document=document, current_node=cell_input)
                with renderer:
                    myst_ast = Document(cell["source"])
                    renderer.render(myst_ast)
            # If a code cell, convert the code + outputs
            elif cell["cell_type"] == "code":
                code_block = literal_block(text=cell["source"])
                cell_input += code_block

                # TODO: currently uses Jupyter-Sphinx and hard-codes outputs in the
                #       docutils tree. We should instead put the mimebundle in the
                #       docutils tree and renderers choose how things are parsed.

                cell_output = container(classes=["cell_output"])
                sphinx_cell += cell_output

                # ==================
                # Cell output
                # ==================
                # TODO: hard-coding the jupyter-sphinx render priority but we should
                #       remove when we refactor
                    # JupyterWidgetViewNode holds widget view JSON,
                # but is only rendered properly in HTML documents.
                # Used to render an element node as HTML
                def visit_element_html(self, node):
                    self.body.append(node.html())
                    raise docutils.nodes.SkipNode

                # Used for nodes that do not need to be rendered
                def skip(self, node):
                    raise docutils.nodes.SkipNode

                self.app.add_node(
                    JupyterWidgetViewNode,
                    html=(visit_element_html, None),
                    latex=(skip, None),
                    textinfo=(skip, None),
                    text=(skip, None),
                    man=(skip, None),
                )
                # JupyterWidgetStateNode holds the widget state JSON,
                # but is only rendered in HTML documents.
                self.app.add_node(
                    JupyterWidgetStateNode,
                    html=(visit_element_html, None),
                    latex=(skip, None),
                    textinfo=(skip, None),
                    text=(skip, None),
                    man=(skip, None),
                )
                WIDGET_VIEW_MIMETYPE = "application/vnd.jupyter.widget-view+json"
                RENDER_PRIORITY = [
                    WIDGET_VIEW_MIMETYPE,
                    "application/javascript",
                    "text/html",
                    "image/svg+xml",
                    "image/png",
                    "image/jpeg",
                    "text/latex",
                    "text/plain",
                ]

                # Write the notebook output to disk if needed
                doc_relpath = os.path.dirname(self.env.docname)  # relative to src dir
                output_dir = os.path.join(output_directory(self.env), doc_relpath)
                write_notebook_output(ntbk, output_dir, notebook_name)

                # Create doctree nodes for cell outputs.
                HAS_STDERR = False  # TODO: Hard code this for now and we'll fix later
                THEBE_CONFIG = {}
                output_nodes = cell_output_to_nodes(
                    cell,
                    RENDER_PRIORITY,
                    HAS_STDERR,
                    sphinx_abs_dir(self.env),
                    THEBE_CONFIG,
                )
                cell_output += output_nodes
