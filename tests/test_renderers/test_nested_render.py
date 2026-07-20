"""Tests for source-attributed nested renders and ``insert_input``.

These cover the supported extension-author API for rendering generated content:

- :meth:`.DocutilsRenderer.nested_render_text` with ``source=`` attributes both
  the rendered nodes' ``source`` and any warnings emitted during the render to a
  caller-specified path (rather than the containing document), and restores the
  previous attribution afterwards (re-entrantly);
- :meth:`.MockStateMachine.insert_input` renders generated MyST at the
  directive's position, with a docutils-compatible signature;
- ``MockState.renderer`` / ``MockStateMachine.renderer`` expose the renderer;
- the ``include`` directive attributes warnings to the included file at the
  correct (off-by-one-fixed) line, in both docutils and sphinx modes.

Docutils-mode tests use ``publish_doctree`` with a ``StringIO`` warning stream
(and ``tmp_path`` where real files are needed); sphinx-mode tests use the
``sphinx_doctree`` fixture from ``sphinx-pytest`` (whose ``.warnings`` normalises
the source directory to ``<src>``).
"""

import contextlib
import io
from collections.abc import Sequence

import pytest
from docutils import nodes
from docutils.core import publish_doctree
from docutils.frontend import get_default_settings
from docutils.parsers.rst import Directive
from docutils.parsers.rst import Parser as RSTParser
from docutils.parsers.rst import directives as rst_directives
from docutils.statemachine import StringList
from docutils.utils import new_document
from sphinx.util.console import strip_colors
from sphinx_pytest.plugin import CreateDoctree

from myst_parser.config.main import MdParserConfig
from myst_parser.mdit_to_docutils.base import DocutilsRenderer, make_document
from myst_parser.parsers.docutils_ import Parser
from myst_parser.parsers.mdit import create_md_parser
from myst_parser.warnings_ import MystWarnings, create_warning


@contextlib.contextmanager
def _registered(**named_directives):
    """Register directives for the duration of the block, then remove them."""
    for name, cls in named_directives.items():
        rst_directives.register_directive(name, cls)
    try:
        yield
    finally:
        for name in named_directives:
            rst_directives._directives.pop(name, None)


def _publish(source, **overrides):
    """Parse ``source`` as MyST, returning (doctree, warning text)."""
    stream = io.StringIO()
    doctree = publish_doctree(
        source,
        parser=Parser(),
        settings_overrides={"warning_stream": stream, **overrides},
    )
    return doctree, stream.getvalue()


# --- test directives ---------------------------------------------------------


class _SourceRender(Directive):
    """Render generated MyST attributed to a fixed fake template path."""

    has_content = False

    def run(self):
        self.state.renderer.nested_render_text(
            "{unknownrole}`x`\n\nmore *text*",
            0,
            source="/fake/template.j2",
        )
        return []


class _InsertInput(Directive):
    """Insert generated MyST at the directive position, attributed to a source."""

    has_content = False
    # overridable by tests to exercise different input container types
    input_lines: Sequence[str] = ["hello *world*"]

    def run(self):
        # the renderer accessors are the supported entry point, and identical
        assert self.state.renderer is self.state_machine.renderer
        self.state_machine.insert_input(self.input_lines, source="/fake/gen.txt")
        return []


class _InsertInputNoSource(Directive):
    """Insert generated MyST rendered in the document's own line-space."""

    has_content = False

    def run(self):
        self.state_machine.insert_input(["plain *text*"])
        return []


class _InsertWarn(Directive):
    """Insert generated MyST that emits a warning (attributed to the source)."""

    has_content = False

    def run(self):
        self.state_machine.insert_input(["{unknownrole}`x`"], source="/fake/gen.txt")
        return []


class _Outer(Directive):
    """Nested source render: renders content that itself renders a source."""

    has_content = False

    def run(self):
        self.state.renderer.nested_render_text(
            "outer para\n\n```{inner}\n```\n\n{unknownrole}`after-inner`",
            0,
            source="/fake/outer.txt",
        )
        return []


class _Inner(Directive):
    has_content = False

    def run(self):
        self.state.renderer.nested_render_text(
            "{unknownrole}`in-inner`", 0, source="/fake/inner.txt"
        )
        return []


class _RaiseAfterRender(Directive):
    """A misbehaving directive that raises after a source render."""

    has_content = False

    def run(self):
        self.state.renderer.nested_render_text("ok text", 0, source="/fake/boom.j2")
        raise ValueError("directive boom")


# =============================================================================
# 1 + 2. include attribution (attribution + off-by-one fix)
# =============================================================================


def test_include_attribution_docutils(tmp_path):
    """A warning inside an included file cites that file, at its true line.

    The unknown directive is on line 3 of ``inc.md``; previously the include
    reported it one line too far (``inc.md:4``).
    """
    tmp_path.joinpath("inc.md").write_text("para\n\n```{unknowndir}\n```\n")
    stream = io.StringIO()
    publish_doctree(
        "# Title\n\n```{include} inc.md\n```\n",
        source_path=str(tmp_path / "index.md"),
        parser=Parser(),
        settings_overrides={"warning_stream": stream},
    )
    warnings = stream.getvalue().replace(str(tmp_path) + "/", "")
    assert "inc.md:3: (WARNING/2) Unknown directive type: 'unknowndir'" in warnings
    # not attributed to the containing document, nor the old off-by-one line
    assert "index.md" not in warnings
    assert "inc.md:4" not in warnings


def test_include_attribution_sphinx(sphinx_doctree: CreateDoctree):
    """Sphinx logs the *included* file (not the parent) at the true line.

    ``inc.md`` is excluded from the build (via ``exclude_patterns``) so it is not
    additionally built as a standalone document, which would emit its own
    (coincidentally identical) warning and mask a mis-attribution.
    """
    sphinx_doctree.srcdir.joinpath("inc.md").write_text(
        "para\n\n```{unknowndir}\n```\n"
    )
    sphinx_doctree.set_conf(
        {"extensions": ["myst_parser"], "exclude_patterns": ["inc.md"]}
    )
    result = sphinx_doctree("# Title\n\n```{include} inc.md\n```\n", "index.md")
    warnings = strip_colors(result.warnings)
    assert "<src>/inc.md:3: WARNING: Unknown directive type: 'unknowndir'" in warnings
    # not the containing document / old off-by-one line
    assert "index.md:4" not in warnings


def test_include_start_after_true_file_line(tmp_path):
    """``:start-after:`` reports the warning at its TRUE file line.

    The included file's ``{unknowndir}`` fence is on file line 5.  Previously
    ``startline`` was advanced by the *character* index of the marker, so the
    warning was reported far past the end of the file (here ``inc.md:32``);
    the fix advances by the number of consumed newlines, giving ``inc.md:5``.
    """
    tmp_path.joinpath("inc.md").write_text(
        "first line\nsecond START-HERE\nthird line\n\n```{unknowndir}\n```\n"
    )
    stream = io.StringIO()
    publish_doctree(
        "# Title\n\n```{include} inc.md\n:start-after: START-HERE\n```\n",
        source_path=str(tmp_path / "index.md"),
        parser=Parser(),
        settings_overrides={"warning_stream": stream},
    )
    warnings = stream.getvalue().replace(str(tmp_path) + "/", "")
    assert "inc.md:5: (WARNING/2) Unknown directive type: 'unknowndir'" in warnings
    # not the old character-index-derived line (past EOF)
    assert "inc.md:32" not in warnings


def test_include_start_after_end_before_true_file_line(tmp_path):
    """Combined ``:start-after:`` + ``:end-before:`` reports the TRUE file line.

    The ``{unknowndir}`` fence is on file line 4, between the ``START`` and
    ``END`` markers.  ``:end-before:`` does not touch ``startline``, so only the
    (now newline-counted) ``:start-after:`` shift applies -- giving ``inc.md:4``
    rather than the old character-index-derived ``inc.md:15``.
    """
    tmp_path.joinpath("inc.md").write_text(
        "header\nSTART\n\n```{unknowndir}\n```\n\nEND\ntrailing\n"
    )
    stream = io.StringIO()
    publish_doctree(
        "# Title\n\n```{include} inc.md\n:start-after: START\n:end-before: END\n```\n",
        source_path=str(tmp_path / "index.md"),
        parser=Parser(),
        settings_overrides={"warning_stream": stream},
    )
    warnings = stream.getvalue().replace(str(tmp_path) + "/", "")
    assert "inc.md:4: (WARNING/2) Unknown directive type: 'unknowndir'" in warnings
    # not the old character-index-derived line
    assert "inc.md:15" not in warnings


# =============================================================================
# 3. extension-style source override (both modes)
# =============================================================================


def test_source_override_docutils():
    """``nested_render_text(source=...)`` attributes warnings and nodes."""
    with _registered(sourcerender=_SourceRender):
        doctree, warnings = _publish("# T\n\n```{sourcerender}\n```\n")
    assert (
        '/fake/template.j2:1: (WARNING/2) Unknown interpreted text role "unknownrole".'
        in warnings
    )
    # node stamping: the rendered paragraph carries the overridden source
    para = next(
        p for p in doctree.findall(nodes.paragraph) if p.astext() == "more text"
    )
    assert para.source == "/fake/template.j2"
    assert para.line == 3  # third line of the rendered text


def test_source_override_sphinx(sphinx_doctree: CreateDoctree):
    """The sphinx logger path attributes to the source string verbatim.

    The location is a colon-containing string, so sphinx does not run it through
    ``doc2path`` (which would resolve the relative template path against the
    source dir).
    """
    sphinx_doctree.set_conf({"extensions": ["myst_parser"]})
    with _registered(sourcerender=_SourceRender):
        result = sphinx_doctree("# T\n\n```{sourcerender}\n```\n", "index.md")
    warnings = strip_colors(result.warnings)
    assert (
        '/fake/template.j2:1: WARNING: Unknown interpreted text role "unknownrole".'
        in warnings
    )
    doctree = result.doctrees["index"]
    para = next(
        p for p in doctree.findall(nodes.paragraph) if p.astext() == "more text"
    )
    assert para.source == "/fake/template.j2"


# =============================================================================
# 4. insert_input
# =============================================================================


@pytest.mark.parametrize(
    "make_input",
    [
        pytest.param(lambda: ["hello *world*"], id="list"),
        pytest.param(
            lambda: StringList(["hello *world*"], source="/fake/gen.txt"),
            id="stringlist",
        ),
    ],
)
def test_insert_input_renders_at_position(make_input, monkeypatch):
    """Inserted content renders at the directive's position, source-attributed.

    ``insert_input`` accepts either a plain ``list[str]`` or a docutils
    ``StringList`` (whose lines are joined), so both produce identical output.
    """
    monkeypatch.setattr(_InsertInput, "input_lines", make_input())
    with _registered(insertinput=_InsertInput):
        doctree, warnings = _publish(
            "# T\n\nbefore\n\n```{insertinput}\n```\n\nafter\n"
        )
    assert not warnings.strip()
    # content is spliced in document order, before any returned nodes
    paras = [p.astext() for p in doctree.findall(nodes.paragraph)]
    assert paras == ["before", "hello world", "after"]
    # the inserted paragraph is attributed to the given source
    hello = next(
        p for p in doctree.findall(nodes.paragraph) if p.astext() == "hello world"
    )
    assert hello.source == "/fake/gen.txt"
    emphasis = next(e for e in doctree.findall(nodes.emphasis))
    assert emphasis.astext() == "world"


def test_insert_input_warning_attribution():
    """A warning from inserted content attributes to ``source:1``."""
    with _registered(insertwarn=_InsertWarn):
        _doctree, warnings = _publish("# T\n\n```{insertwarn}\n```\n")
    assert (
        '/fake/gen.txt:1: (WARNING/2) Unknown interpreted text role "unknownrole".'
        in warnings
    )


def test_insert_input_no_source_document_space():
    """Without ``source``, inserted content renders in the document's space."""
    with _registered(insertnosource=_InsertInputNoSource):
        doctree, warnings = _publish("# T\n\n```{insertnosource}\n```\n")
    assert not warnings.strip()
    para = next(
        p for p in doctree.findall(nodes.paragraph) if p.astext() == "plain text"
    )
    # attributed to the document itself (no override), not a separate source
    assert para.source == "<string>"


def test_renderer_properties_are_the_renderer():
    """``MockState.renderer`` and ``MockStateMachine.renderer`` are the renderer."""
    captured = {}

    class _Capture(Directive):
        has_content = False

        def run(self):
            captured["state"] = self.state.renderer
            captured["machine"] = self.state_machine.renderer
            captured["is_renderer"] = isinstance(self.state.renderer, DocutilsRenderer)
            return []

    with _registered(capturerenderer=_Capture):
        _publish("```{capturerenderer}\n```\n")
    assert captured["is_renderer"]
    assert captured["state"] is captured["machine"]


# =============================================================================
# 5. restoration (success path, nesting, and exception path)
# =============================================================================


def test_nested_source_render_attributes_innermost_and_restores():
    """Nested source renders attribute innermost, and restore outward.

    An ``{outer}`` render (source ``outer.txt``) contains an ``{inner}`` render
    (source ``inner.txt``); the inner warning cites ``inner.txt`` and, after it
    returns, the outer render's warning cites ``outer.txt`` again.  After the
    whole directive a document-level warning attributes to the document.
    """
    source = "# T\n\n```{outer}\n```\n\n{unknownrole}`doc-level`\n"
    with _registered(outer=_Outer, inner=_Inner):
        _doctree, warnings = _publish(source)
    # innermost attributed to inner.txt (line 1 of the inner render)
    assert "/fake/inner.txt:1: (WARNING/2) Unknown interpreted text role" in warnings
    # restored outward to outer.txt for content after the inner render (line 6)
    assert "/fake/outer.txt:6: (WARNING/2) Unknown interpreted text role" in warnings
    # restored to the document for a warning after the directive (line 6)
    assert '<string>:6: (WARNING/2) Unknown interpreted text role "unknownrole".' in (
        warnings
    )


def test_source_restored_after_directive_raises():
    """A directive raising after a source render leaves the document restored.

    The source override lives inside ``nested_render_text`` (which completes
    before the raise), so a subsequent document warning attributes to the
    document, and ``document["source"]`` is the original.
    """

    class _Guard(Directive):
        has_content = False

        def run(self):
            try:
                self.state.renderer.nested_render_text(
                    "ok text", 0, source="/fake/boom.j2"
                )
            finally:
                # capture state immediately after the source render returns
                _Guard.doc_source_after = self.state.renderer.document["source"]
                _Guard.stack_after = list(self.state.renderer._attribution_sources)
            return []

    with _registered(guard=_Guard):
        _doctree, warnings = _publish(
            "# T\n\n```{guard}\n```\n\n{unknownrole}`later`\n"
        )
    assert _Guard.doc_source_after == "<string>"
    assert _Guard.stack_after == []
    # the later document warning attributes to the document, not the source
    assert '<string>:6: (WARNING/2) Unknown interpreted text role "unknownrole".' in (
        warnings
    )
    assert "/fake/boom.j2" not in warnings


def test_nested_render_text_restores_on_exception(monkeypatch):
    """The source override is restored even if the render raises mid-way."""
    md = create_md_parser(MdParserConfig(), DocutilsRenderer)
    document = make_document("orig.md")
    md.options["document"] = document
    renderer = md.renderer
    renderer.setup_render(md.options, {})

    orig_source = renderer.document["source"]
    orig_reporter_source = renderer.reporter.source
    orig_has_gsl = hasattr(renderer.reporter, "get_source_and_line")

    def boom(_tokens):
        # the override must be active while rendering...
        assert renderer.document["source"] == "/fake/s.txt"
        assert renderer.reporter.source == "/fake/s.txt"
        assert renderer._attribution_sources == ["/fake/s.txt"]
        raise RuntimeError("render boom")

    monkeypatch.setattr(renderer, "_render_tokens", boom)

    with pytest.raises(RuntimeError, match="render boom"):
        renderer.nested_render_text("x", 0, source="/fake/s.txt")

    # ...and fully restored afterwards
    assert renderer.document["source"] == orig_source
    assert renderer.reporter.source == orig_reporter_source
    assert hasattr(renderer.reporter, "get_source_and_line") == orig_has_gsl
    assert renderer._attribution_sources == []


# =============================================================================
# 6. create_warning ``source`` kwarg is standalone-load-bearing (override-free)
# =============================================================================
#
# The extension-style tests above always run with the renderer's ambient
# reporter override active (set by ``nested_render_text(source=...)``), which
# would mask ``create_warning``'s own ``source`` handling.  These call
# ``create_warning`` directly, with no override in play, so the ``source``
# kwarg is the only thing that can move the attribution.


def _override_free_document(stream):
    """A docutils-mode document with a fresh reporter and no source override."""
    settings = get_default_settings(RSTParser)
    settings.warning_stream = stream
    settings.myst_suppress_warnings = []
    return new_document("mydoc.md", settings)


@pytest.mark.parametrize(
    "line,expected",
    [(3, "/fake/x.txt:3:"), (None, "/fake/x.txt:")],
    ids=["with-line", "no-line"],
)
def test_create_warning_source_docutils_arm(line, expected):
    """``create_warning(source=...)`` attributes via the docutils reporter arm.

    There is no renderer (hence no ambient reporter override), so the ``source``
    kwarg passed through to ``reporter.warning`` is the only thing that can move
    the attribution off the document's own source -- i.e. it is
    standalone-load-bearing.
    """
    stream = io.StringIO()
    document = _override_free_document(stream)
    create_warning(
        document, "msg", MystWarnings.RENDER_METHOD, source="/fake/x.txt", line=line
    )
    warnings = stream.getvalue()
    assert expected in warnings
    # the document's own source must not leak in (proves the kwarg is honoured)
    assert "mydoc.md" not in warnings


class _SphinxSourceWarnNoLine(Directive):
    """Emit a source-attributed, line-less warning through ``create_warning``."""

    has_content = False

    def run(self):
        create_warning(
            self.state.document,
            "no-line msg",
            MystWarnings.RENDER_METHOD,
            source="/fake/x.txt",
            line=None,
        )
        return []


def test_create_warning_source_sphinx_arm_no_line(sphinx_doctree: CreateDoctree):
    """The sphinx arm logs ``source:`` (trailing colon) and skips ``doc2path``.

    With ``line=None`` the location is the string ``"/fake/x.txt:"``; the
    trailing colon makes sphinx pass it through verbatim rather than resolving
    it as a docname (which would append a source suffix such as ``.rst``).
    """
    sphinx_doctree.set_conf({"extensions": ["myst_parser"]})
    with _registered(swarn=_SphinxSourceWarnNoLine):
        result = sphinx_doctree("# T\n\n```{swarn}\n```\n", "index.md")
    warnings = strip_colors(result.warnings)
    assert "/fake/x.txt:: WARNING: no-line msg" in warnings
    # not doc2path-mangled into a docname with a source suffix
    assert ".rst" not in warnings
