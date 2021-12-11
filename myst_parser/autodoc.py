"""Overrides for autodoc functionality."""
from typing import List, Type

from docutils.nodes import Node
from docutils.statemachine import StringList
from sphinx.application import Sphinx
from sphinx.config import ENUM
from sphinx.ext.autodoc import Documenter
from sphinx.ext.autodoc.directive import (
    AutodocDirective,
    DocumenterBridge,
    DummyOptionSpec,
    logger,
    parse_generated_content,
    process_documenter_options,
)
from sphinx.util.docutils import SphinxDirective

from myst_parser.mocking import MockState


class MystAutodocDirective(SphinxDirective):
    """A directive class for all autodoc directives. It works as a dispatcher of Documenters.

    It invokes a Documenter on running. After the processing, it parses and returns
    the generated content by Documenter.
    """

    option_spec = DummyOptionSpec()
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True

    def run(self) -> List[Node]:
        reporter = self.state.document.reporter

        try:
            source, lineno = reporter.get_source_and_line(self.lineno)
        except AttributeError:
            source, lineno = (None, None)
        logger.debug("[autodoc] %s:%s: input:\n%s", source, lineno, self.block_text)

        # look up target Documenter
        objtype = self.name[4:]  # strip prefix (auto-).
        doccls: Type[Documenter] = self.env.app.registry.documenters[objtype]

        # process the options with the selected documenter's option_spec
        try:
            documenter_options = process_documenter_options(
                doccls, self.config, self.options
            )
        except (KeyError, ValueError, TypeError) as exc:
            # an option is either unknown or has a wrong type
            logger.error(
                "An option to %s is either unknown or has an invalid value: %s"
                % (self.name, exc),
                location=(self.env.docname, lineno),
            )
            return []

        # generate the output
        params = DocumenterBridge(
            self.env, reporter, documenter_options, lineno, self.state
        )
        documenter = doccls(params, self.arguments[0])
        documenter.generate(more_content=self.content)
        if not params.result:
            return []

        logger.debug("[autodoc] output:\n%s", "\n".join(params.result))

        # record all filenames as dependencies -- this will at least
        # partially make automatic invalidation possible

        # sphinx v3 -> v4: filename_set -> record_dependencies
        for fn in getattr(params, "record_dependencies", params.filename_set):
            self.state.document.settings.record_dependencies.add(fn)

        content = preprocess_content("\n".join(params.result), self, documenter)
        string = StringList(content.splitlines())

        result = parse_generated_content(self.state, string, documenter)

        result = postprocess_nodes(result)

        return result


def preprocess_content(
    content: str, inst: MystAutodocDirective, documenter: Documenter
) -> str:
    """Preprocess the content."""
    # test if parsing within a MyST Parser
    if isinstance(inst.state, MockState):
        if inst.config.myst_autodoc_format == "myst":
            raise NotImplementedError("MyST autodoc format is not implemented yet.")
        return "```{eval-rst}\n\n" + content + "\n```"
    # else assume RST
    return content


def postprocess_nodes(nodes: List[Node]) -> List[Node]:
    """Postprocess the nodes."""
    return nodes


def setup(app: Sphinx):
    """Register the directive with Sphinx."""
    app.add_config_value("myst_autodoc_format", "rst", "env", ENUM("myst", "rst"))
    app.add_directive("myst-autodoc", MystAutodocDirective)
    from docutils.parsers.rst.directives import _directives

    for name, objtype in _directives.items():
        if objtype == AutodocDirective:
            app.add_directive(name, MystAutodocDirective, override=True)
