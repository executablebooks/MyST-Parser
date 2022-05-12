"""Code to use internally, for documentation."""
from __future__ import annotations

import io
from typing import Sequence, Union

from docutils import nodes
from docutils.frontend import OptionParser
from docutils.parsers.rst import directives
from sphinx.directives import other
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective
from typing_extensions import get_args, get_origin

from .config.main import MdParserConfig
from .parsers.docutils_ import Parser as DocutilsParser

logger = logging.getLogger(__name__)


class _ConfigBase(SphinxDirective):
    """Directive to automate rendering of the configuration."""

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
        "extensions": directives.flag,
        "scope": lambda x: directives.choice(x, ["global", "local"]),
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

            if "extensions" in self.options:
                if not field.metadata.get("extension"):
                    continue
            else:
                if field.metadata.get("extension"):
                    continue

            if self.options.get("scope") == "local":
                if field.metadata.get("global_only"):
                    continue

            if self.options.get("scope") == "global":
                name = f"myst_{name}"

            description = " ".join(field.metadata.get("help", "").splitlines())
            if field.metadata.get("extension"):
                description = f"{field.metadata.get('extension')}: {description}"
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
        stream = io.StringIO()
        OptionParser(
            components=(DocutilsParser,),
            usage="myst-docutils-<writer> [options] [<source> [<destination>]]",
        ).print_help(stream)
        return [nodes.literal_block("", stream.getvalue())]


class DirectiveDoc(SphinxDirective):
    """Load and document a directive."""

    required_arguments = 1  # name of the directive
    has_content = True

    def run(self):
        """Run the directive."""
        name = self.arguments[0]
        # load the directive class
        klass, _ = directives.directive(
            name, self.state.memo.language, self.state.document
        )
        if klass is None:
            logger.warning(f"Directive {name} not found.", line=self.lineno)
            return []
        content = " ".join(self.content)
        text = f"""\
:Name: `{name}`
:Description: {content}
:Arguments: {klass.required_arguments} required, {klass.optional_arguments} optional
:Content: {'yes' if klass.has_content else 'no'}
:Options:
"""
        if klass.option_spec:
            text += "  name | type\n  -----|------\n"
            for key, func in klass.option_spec.items():
                text += f"  {key} | {convert_opt(name, func)}\n"
        node = nodes.Element()
        self.state.nested_parse(text.splitlines(), 0, node)
        return node.children


def convert_opt(name, func):
    """Convert an option function to a string."""
    if func is directives.flag:
        return "flag"
    if func is directives.unchanged:
        return "text"
    if func is directives.unchanged_required:
        return "text"
    if func is directives.class_option:
        return "space-delimited list"
    if func is directives.uri:
        return "URI"
    if func is directives.path:
        return "path"
    if func is int:
        return "integer"
    if func is directives.positive_int:
        return "integer (positive)"
    if func is directives.nonnegative_int:
        return "integer (non-negative)"
    if func is directives.positive_int_list:
        return "space/comma-delimited list of integers (positive)"
    if func is directives.percentage:
        return "percentage"
    if func is directives.length_or_unitless:
        return "length or unitless"
    if func is directives.length_or_percentage_or_unitless:
        return "length, percentage or unitless"
    if func is other.int_or_nothing:
        return "integer"
    return ""
