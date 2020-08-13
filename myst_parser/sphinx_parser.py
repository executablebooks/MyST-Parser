from os import path
import time

from docutils import frontend, nodes
from docutils.core import publish_doctree
from sphinx.application import Sphinx
from sphinx.io import SphinxStandaloneReader
from sphinx.parsers import Parser
from sphinx.util import logging
from sphinx.util.docutils import sphinx_domains

from myst_parser.main import default_parser


SPHINX_LOGGER = logging.getLogger(__name__)


class MystParser(Parser):
    """Docutils parser for Markedly Structured Text (MyST)."""

    supported = ("md", "markdown", "myst")
    translate_section_name = None

    default_config = {
        "myst_disable_syntax": (),
        "myst_url_schemes": None,
        "myst_math_delimiters": "dollars",
        "myst_amsmath_enable": False,
        "myst_admonition_enable": False,
        "myst_html_img": False,
    }

    # these specs are copied verbatim from the docutils RST parser
    settings_spec = (
        "MyST Parser Options",
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

    def parse(
        self, inputstring: str, document: nodes.document, renderer: str = "sphinx"
    ):
        """Parse source text.

        :param inputstring: The source string to parse
        :param document: The root docutils node to add AST elements to
        """
        if renderer == "sphinx":
            config = document.settings.env.app.config
        else:
            config = self.default_config.copy()
        parser = self.get_markdown_parser(config, renderer)
        parser.options["document"] = document
        parser.render(inputstring)

    @staticmethod
    def get_markdown_parser(config: dict, renderer: str = "sphinx"):

        parser = default_parser(
            renderer=renderer,
            disable_syntax=config["myst_disable_syntax"],
            math_delimiters=config["myst_math_delimiters"],
            enable_amsmath=config["myst_amsmath_enable"],
            enable_admonitions=config["myst_admonition_enable"],
        )
        parser.options.update(
            {
                "myst_url_schemes": config["myst_url_schemes"],
                "myst_html_img": config["myst_html_img"],
            }
        )
        return parser


def parse(app: Sphinx, text: str, docname: str = "index") -> nodes.document:
    """Parse a string as MystMarkdown with Sphinx application."""
    app.env.temp_data["docname"] = docname
    app.env.all_docs[docname] = time.time()
    reader = SphinxStandaloneReader()
    reader.setup(app)
    parser = MystParser()
    parser.set_application(app)
    with sphinx_domains(app.env):
        return publish_doctree(
            text,
            path.join(app.srcdir, docname + ".md"),
            reader=reader,
            parser=parser,
            parser_name="markdown",
            settings_overrides={"env": app.env, "gettext_compact": True},
        )
