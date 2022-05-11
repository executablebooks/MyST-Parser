"""Directives for use internally, to document the configuration."""
from __future__ import annotations

from typing import Sequence, Union

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective
from typing_extensions import get_args, get_origin

from .main import MdParserConfig


class _ConfigBase(SphinxDirective):
    """Directive to automate printing of the configuration."""

    @staticmethod
    def table_header():
        return [
            "```````{list-table}",
            ":header-rows: 1",
            ":widths: 15 10 20",
            "",
            "* - Name",
            "  - Type",
            "  - Description",
        ]

    @staticmethod
    def field_default(value):
        default = " ".join(f"{value!r}".splitlines())
        # if len(default) > 20:
        #     default = default[:20] + "..."
        return default

    @staticmethod
    def field_type(field):
        ftypes: Sequence[str]
        if get_origin(field.type) is Union:
            ftypes = get_args(field.type)
        else:
            ftypes = [field.type]
        ctype = " | ".join(
            str("None" if ftype == type(None) else ftype)  # type: ignore  # noqa: E721
            for ftype in ftypes
        )
        ctype = " ".join(ctype.splitlines())
        ctype = ctype.replace("typing.", "")
        ctype = ctype.replace("typing_extensions.", "")
        for tname in ("str", "int", "float", "bool"):
            ctype = ctype.replace(f"<class '{tname}'>", tname)
        return ctype


class MystConfigDirective(_ConfigBase):

    option_spec = {
        "sphinx": directives.flag,
    }

    def run(self):
        """Run the directive."""
        config = MdParserConfig()
        text = self.table_header()
        count = 0
        for name, value, field in config.as_triple():

            # filter by sphinx options
            if "sphinx" in self.options and field.metadata.get("sphinx_exclude"):
                continue

            name = f"myst_{name}"
            description = " ".join(field.metadata.get("help", "").splitlines())
            default = self.field_default(value)
            ctype = self.field_type(field)
            text.extend(
                [
                    f"* - `{name}`",
                    f"  - `{ctype}`",
                    f"  - {description} (default: `{default}`)",
                ]
            )

            count += 1

        if not count:
            return []

        text.append("```````")
        node = nodes.Element()
        self.state.nested_parse(text, 0, node)
        return node.children


class DocutilsCliHelpDirective(SphinxDirective):
    """Directive to print the docutils CLI help."""

    has_content = False
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False

    def run(self):
        """Run the directive."""
        import io

        from docutils import nodes
        from docutils.frontend import OptionParser

        from myst_parser.parsers.docutils_ import Parser as DocutilsParser

        stream = io.StringIO()
        OptionParser(
            components=(DocutilsParser,),
            usage="myst-docutils-<writer> [options] [<source> [<destination>]]",
        ).print_help(stream)
        return [nodes.literal_block("", stream.getvalue())]
