"""Tests for document-relative directive line mapping (docutils convention).

A directive at any document position must receive a ``content_offset`` such
that ``content_offset + N`` maps its Nth (1-based) content line to the true
1-based document line. Equivalently, ``content_offset`` is the 0-based
*absolute* document line of the first content line (``(1-based line) - 1``),
and each entry of ``content.items`` carries the 0-based absolute document line
of its line. This mirrors what docutils' own rST parser provides, so that
extensions computing ``content_offset + N`` (e.g. sphinx-jinja2) report the
correct line under MyST too.
"""

import contextlib
import io

import pytest
from docutils import nodes
from docutils.core import publish_doctree
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives as rst_directives

from myst_parser.parsers.docutils_ import Parser

# module-level sink the capture directives append to (cleared per run)
_CAPTURED: list[dict] = []


class _Capture(Directive):
    """Record a directive's line-mapping data, then nested-parse its content."""

    has_content = True
    option_spec = {
        "opt": rst_directives.unchanged,
        "class": rst_directives.class_option,
        "name": rst_directives.unchanged,
    }

    def run(self):
        _CAPTURED.append(
            {
                "lineno": self.lineno,
                "content_offset": self.content_offset,
                "content": list(self.content),
                "items": list(self.content.items),
            }
        )
        # a standard nested parse, so nested node lines can be observed too
        node = nodes.Element()
        self.state.nested_parse(self.content, self.content_offset, node)
        return list(node.children)


class _CaptureArg(_Capture):
    """Capture variant that takes a single (whitespace) argument."""

    optional_arguments = 1
    final_argument_whitespace = True


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


def _run_myst(source, *, extensions=None):
    """Parse ``source`` as MyST and return (captured, doctree)."""
    _CAPTURED.clear()
    overrides = {"warning_stream": io.StringIO()}
    if extensions:
        overrides["myst_enable_extensions"] = extensions
    with _registered(cap=_Capture, caparg=_CaptureArg):
        doctree = publish_doctree(source, parser=Parser(), settings_overrides=overrides)
    return list(_CAPTURED), doctree


def _run_rst(source):
    """Parse ``source`` with the plain docutils rST parser (ground truth)."""
    _CAPTURED.clear()
    with _registered(cap=_Capture, caparg=_CaptureArg):
        doctree = publish_doctree(
            source, settings_overrides={"warning_stream": io.StringIO()}
        )
    return list(_CAPTURED), doctree


def _publish(source, *, extensions=None):
    """Parse ``source`` as MyST and return (doctree, stripped warnings)."""
    overrides = {"warning_stream": io.StringIO()}
    if extensions:
        overrides["myst_enable_extensions"] = extensions
    doctree = publish_doctree(source, parser=Parser(), settings_overrides=overrides)
    return doctree, overrides["warning_stream"].getvalue().strip()


def _assert_docutils_convention(cap):
    """Assert a capture obeys the docutils ``content_offset``/``items`` contract."""
    length = len(cap["content"])
    if length:
        source = cap["items"][0][0]
        # items are one-per-line, each the 0-based absolute document line
        assert cap["items"] == [
            (source, cap["content_offset"] + i) for i in range(length)
        ]
        # content_offset is the 0-based absolute line of the first content line
        assert cap["content_offset"] == cap["items"][0][1]
    else:
        assert cap["items"] == []


# Each case: (source, extensions, expected) where ``expected`` is a list of
# (lineno, first_content_line, content) per captured directive, in run order.
# ``first_content_line`` is the true 1-based document line of the first content
# line, so the expected ``content_offset`` is ``first_content_line - 1``.
_MYST_SHAPES = [
    pytest.param(
        # 1:```{cap}  2:hello world  3:```
        "```{cap}\nhello world\n```\n",
        None,
        [(1, 2, ["hello world"])],
        id="bare-pos1",
    ),
    pytest.param(
        # 1:# Title 2: 3:para 4: 5:```{cap} 6:hello world 7:```
        "# Title\n\npara\n\n```{cap}\nhello world\n```\n",
        None,
        [(5, 6, ["hello world"])],
        id="bare-pos2",
    ),
    pytest.param(
        # 1:```{cap} hello world  2:```
        "```{cap} hello world\n```\n",
        None,
        [(1, 1, ["hello world"])],
        id="merged-first-line",
    ),
    pytest.param(
        # 1:```{caparg} myarg  2:content here  3:```
        "```{caparg} myarg\ncontent here\n```\n",
        None,
        [(1, 2, ["content here"])],
        id="argument",
    ),
    pytest.param(
        # 1:```{cap} 2::opt: xx 3::class: cc 4:content here 5:```
        "```{cap}\n:opt: xx\n:class: cc\ncontent here\n```\n",
        None,
        [(1, 4, ["content here"])],
        id="options-pos1",
    ),
    pytest.param(
        # 1:intro 2: 3:```{cap} 4::opt: xx 5::class: cc 6:body 7:```
        "intro\n\n```{cap}\n:opt: xx\n:class: cc\nbody\n```\n",
        None,
        [(3, 6, ["body"])],
        id="options-pos2",
    ),
    pytest.param(
        # 1:```{cap} 2::opt: xx 3::class: cc 4:(blank) 5:content here 6:```
        "```{cap}\n:opt: xx\n:class: cc\n\ncontent here\n```\n",
        None,
        [(1, 5, ["content here"])],
        id="options-blank",
    ),
    pytest.param(
        # 1:```{cap} 2:--- 3:opt: xx 4:class: cc 5:--- 6:content here 7:```
        "```{cap}\n---\nopt: xx\nclass: cc\n---\ncontent here\n```\n",
        None,
        [(1, 6, ["content here"])],
        id="yaml-block",
    ),
    pytest.param(
        # 1:before 2: 3::::{cap} 4:colon content 5::::
        "before\n\n:::{cap}\ncolon content\n:::\n",
        ["colon_fence"],
        [(3, 4, ["colon content"])],
        id="colon-fence",
    ),
    pytest.param(
        # 1:intro 2: 3:````{cap} 4:(blank) 5:```{cap} 6:inner content 7:``` 8:````
        "intro para\n\n````{cap}\n\n```{cap}\ninner content\n```\n````\n",
        None,
        [
            (3, 5, ["```{cap}", "inner content", "```"]),
            (5, 6, ["inner content"]),
        ],
        id="nested-fence",
    ),
    pytest.param(
        # 1:para before 2: 3:- list item 4: 5:  ```{cap} 6:  nested 7:  ```
        "para before\n\n- list item text\n\n  ```{cap}\n  nested in list\n  ```\n",
        None,
        [(5, 6, ["nested in list"])],
        id="list-embedded",
    ),
]


@pytest.mark.parametrize("source,extensions,expected", _MYST_SHAPES)
def test_myst_content_offset_document_relative(source, extensions, expected):
    """``content_offset`` and ``content.items`` are document-relative (0-based)."""
    caps, _doctree = _run_myst(source, extensions=extensions)
    assert len(caps) == len(expected)
    for cap, (lineno, first_content_line, content) in zip(caps, expected, strict=True):
        assert cap["lineno"] == lineno
        assert cap["content"] == content
        # content_offset == (1-based first content line) - 1
        assert cap["content_offset"] == first_content_line - 1
        _assert_docutils_convention(cap)


@pytest.mark.parametrize(
    "source,first_content_line",
    [
        # 1:.. cap:: 2:(blank) 3:   content here
        (".. cap::\n\n   content here\n", 3),
        # 1:.. cap:: 2:   :opt: 3:   :class: 4:(blank) 5:   content here
        (".. cap::\n   :opt: xx\n   :class: cc\n\n   content here\n", 5),
        # 1:Title 2:===== 3: 4:para 5: 6:.. cap:: 7: 8:   deep content
        ("Title\n=====\n\npara\n\n.. cap::\n\n   deep content\n", 8),
    ],
)
def test_rst_ground_truth_convention(source, first_content_line):
    """The plain docutils rST parser follows the same convention MyST now does.

    This pins the *contract* (``content_offset == first content line - 1`` and
    absolute per-line ``items``) rather than frozen numbers, so MyST parity is
    asserted against docutils itself.
    """
    caps, _doctree = _run_rst(source)
    assert len(caps) == 1
    cap = caps[0]
    assert cap["content_offset"] == first_content_line - 1
    _assert_docutils_convention(cap)


def test_eval_rst_content_offset_pinned():
    """``eval-rst`` already uses the real rST state machine (document-relative)."""
    source = (
        "# Heading\n\npara one\n\npara two\n\n"
        "```{eval-rst}\n.. cap::\n\n   rst inner content\n```\n"
    )
    caps, _doctree = _run_myst(source)
    assert len(caps) == 1
    cap = caps[0]
    # eval-rst fence on line 7, ``.. cap::`` on line 8, content on line 10
    assert cap["lineno"] == 8
    assert cap["content_offset"] == 9
    assert cap["content"] == ["rst inner content"]
    _assert_docutils_convention(cap)


class _WarnAtFirstContentLine(Directive):
    """Mimic an extension reporting a problem on its first content line."""

    has_content = True
    option_spec = {
        "opt": rst_directives.unchanged,
        "class": rst_directives.class_option,
    }

    def run(self):
        # ``content_offset + N`` for the Nth (1-based) content line, i.e. N=1
        self.state_machine.reporter.warning("boom", line=self.content_offset + 1)
        return []


@pytest.mark.parametrize(
    "source,true_line,old_wrong_line",
    [
        # fence on line 1, content on line 2 (old body-relative offset 0 -> line 1)
        ("```{warnat}\nbody\n```\n", 2, 1),
        # fence on line 5, content on line 6 (old body-relative offset 0 -> line 1)
        ("a\n\nb\n\n```{warnat}\nbody\n```\n", 6, 1),
        # fence on line 1, options on 2-3, content on line 4
        # (old body-relative offset 2 -> line 3)
        ("```{warnat}\n:opt: x\n:class: c\nbody\n```\n", 4, 3),
    ],
)
def test_downstream_reporter_warning_line(source, true_line, old_wrong_line):
    """A ``reporter.warning(line=content_offset + N)`` cites the true document line.

    This is the definition of done: the sphinx-jinja2 style idiom must now map
    to ``<string>:TRUELINE:`` for the offending content line.  It must *also*
    no longer emit the old, body-relative ``<string>:{body_offset + 1}:`` line
    (when ``content_offset`` was the relative ``body_offset``).
    """
    stream = io.StringIO()
    with _registered(warnat=_WarnAtFirstContentLine):
        publish_doctree(
            source, parser=Parser(), settings_overrides={"warning_stream": stream}
        )
    warnings = stream.getvalue()
    assert f"<string>:{true_line}:" in warnings
    # the old body-relative location must be gone (skip if it coincides with the
    # true line -- it does not for any case here, but guard against it anyway)
    if old_wrong_line != true_line:
        assert f"<string>:{old_wrong_line}:" not in warnings


@pytest.mark.parametrize(
    "source,note_body_line",
    [
        # note fence on line 1, body on line 2
        ("```{note}\nnote body\n```\n", 2),
        # note fence on line 5, body on line 6
        ("# Title\n\npara\n\n```{note}\nnote body\n```\n", 6),
    ],
)
def test_nested_content_line_unchanged(source, note_body_line):
    """Nested rendering keeps its (already correct) line numbers.

    The document-relative ``content_offset`` change must not shift the lines of
    nested content -- the ``nested_parse`` identity holds for the standard idiom.
    """
    doctree, _warnings = _publish(source)
    para = next(
        p for p in doctree.findall(nodes.paragraph) if p.astext() == "note body"
    )
    assert para.line == note_body_line


def test_epigraph_attribution_line_docutils_parity():
    """``{epigraph}`` attribution ``.line`` matches the docutils rST convention.

    Previously the attribution line was one too small (a latent off-by-one);
    it now equals the attribution's true document line, exactly as the plain
    rST parser reports it.
    """
    # fence on line 3, quoted line 4, blank 5, attribution on document line 6
    source = "before\n\n```{epigraph}\nquoted line\n\n-- Attribution Author\n```\n"
    doctree, _warnings = _publish(source)
    attribution = next(doctree.findall(nodes.attribution))
    quoted = next(
        p for p in doctree.findall(nodes.paragraph) if p.astext() == "quoted line"
    )
    assert attribution.line == 6  # true document line of the attribution
    assert quoted.line == 4  # nested body line is unchanged

    # docutils ground truth: attribution .line == its own document line (here 5)
    rst = ".. epigraph::\n\n   quoted line\n\n   -- Attribution Author\n"
    rst_doctree = publish_doctree(
        rst, settings_overrides={"warning_stream": io.StringIO()}
    )
    rst_attribution = next(rst_doctree.findall(nodes.attribution))
    assert rst_attribution.line == 5


def test_parsed_literal_line_absolute():
    """``{parsed-literal}`` node ``.line`` is now the correct absolute line.

    docutils sets ``node.line = content_offset + 1``; with a document-relative
    ``content_offset`` this is the true content line (previously a hardcoded 1).
    """
    # fence on line 3, content on line 4
    source = "before\n\n```{parsed-literal}\nliteral content\n```\n"
    doctree, _warnings = _publish(source)
    literal = next(doctree.findall(nodes.literal_block))
    assert literal.line == 4


def test_role_directive_smoke():
    """``{role}`` definitions still register cleanly (no regression).

    The docutils ``Role`` directive guards on ``content_offset > lineno``; with
    the merged role spec this never trips, so plain and ``:class:`` forms both
    register and remain usable.
    """
    # plain custom role registers and is usable
    doctree, warnings = _publish("```{role} myrole(emphasis)\n```\n\n{myrole}`hi`\n")
    assert warnings == ""
    assert len(list(doctree.findall(nodes.emphasis))) == 1

    # custom role carrying a :class: option also registers without regression
    doctree, warnings = _publish(
        "```{role} myrole2(emphasis)\n:class: myclass\n```\n\n{myrole2}`hi`\n"
    )
    assert warnings == ""
    emphasis = list(doctree.findall(nodes.emphasis))
    assert len(emphasis) == 1
    assert emphasis[0]["classes"] == ["myclass"]
