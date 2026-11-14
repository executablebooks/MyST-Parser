import contextlib
import importlib.util
import io
import re
import sys
from dataclasses import dataclass, field, fields
from textwrap import dedent
from typing import Literal

import markdown_it.main
import pytest
from docutils import __version_info__ as docutils_version
from docutils import nodes
from docutils.core import publish_doctree, publish_string
from docutils.writers.latex2e import Writer as LatexWriter
from markdown_it.token import Token

from myst_parser.config.main import MdParserConfig
from myst_parser.mdit_to_docutils.base import DocutilsRenderer, make_document
from myst_parser.parsers.docutils_ import (
    Parser,
    attr_to_optparse_option,
    cli_html,
    cli_html5,
    cli_html5_demo,
    cli_latex,
    cli_pseudoxml,
    cli_xml,
    to_html5_demo,
)
from myst_parser.parsers.mdit import (
    DEFAULT_SMARTQUOTES,
    create_md_parser,
    resolve_smartquotes,
)


def test_attr_to_optparse_option():
    @dataclass
    class Config:
        name: Literal["a"] = field(default="default")

    output = attr_to_optparse_option(fields(Config)[0], "default")
    assert len(output) == 3


def test_parser():
    """Test calling `Parser.parse` directly."""
    parser = Parser()
    document = make_document(parser_cls=Parser)
    parser.parse("something", document)
    assert (
        document.pformat().strip()
        == '<document source="notset">\n    <paragraph>\n        something'
    )


def test_parsed_literal_preserves_line_edge_whitespace():
    """Line-edge whitespace survives inline parsing in parsed literals."""
    source = "\n".join(
        [
            "```{parsed-literal}",
            "  first",
            "123",
            " 23",
            "",
            "\t**3**  ",
            "```",
            "",
        ]
    )
    document = publish_doctree(source, parser=Parser())

    literal = next(document.findall(nodes.literal_block))
    assert literal.astext() == "  first\n123\n 23\n\n\t3  "
    assert [node.astext() for node in literal.findall(nodes.strong)] == ["3"]


def test_parsed_literal_whitespace_preserves_delimiter_boundaries():
    """Whitespace remains visible to CommonMark delimiter classification."""
    source = "\n".join(["```{parsed-literal}", "foo *  ", "bar*", "```", ""])
    document = publish_doctree(source, parser=Parser())

    literal = next(document.findall(nodes.literal_block))
    assert literal.astext() == "foo *  \nbar*"
    assert not list(literal.findall(nodes.emphasis))


def test_cli_html(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.TextIOWrapper(io.BytesIO(b"text")))
    cli_html([])
    captured = capsys.readouterr()
    assert not captured.err
    assert "text" in captured.out


def test_cli_html5(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.TextIOWrapper(io.BytesIO(b"text")))
    cli_html5([])
    captured = capsys.readouterr()
    assert not captured.err
    assert "text" in captured.out


def test_cli_html5_demo(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.TextIOWrapper(io.BytesIO(b"text")))
    cli_html5_demo([])
    captured = capsys.readouterr()
    assert not captured.err
    assert "text" in captured.out


def test_to_html5_demo():
    assert to_html5_demo("text").strip() == "<p>text</p>"


def test_cli_latex(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.TextIOWrapper(io.BytesIO(b"text")))
    cli_latex([])
    captured = capsys.readouterr()
    assert not captured.err
    assert "text" in captured.out


def test_cli_xml(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.TextIOWrapper(io.BytesIO(b"text")))
    cli_xml([])
    captured = capsys.readouterr()
    assert not captured.err
    assert "text" in captured.out


def test_cli_pseudoxml(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.TextIOWrapper(io.BytesIO(b"text")))
    cli_pseudoxml([])
    captured = capsys.readouterr()
    assert not captured.err
    assert "text" in captured.out


def test_help_text():
    """Test retrieving settings help text."""
    from docutils.core import Publisher

    stream = io.StringIO()
    pub = Publisher(parser=Parser())
    with contextlib.redirect_stdout(stream):
        try:
            pub.process_command_line(["--help"])
        except SystemExit as exc:
            assert not exc.code

    assert "MyST options" in stream.getvalue()
    # the option's help text is its only user-facing documentation
    assert 'rel="noreferrer noopener"' in " ".join(stream.getvalue().split())


def test_include_from_rst(tmp_path):
    """Test including a MyST file from within an RST file."""
    from docutils.parsers.rst import Parser as RSTParser

    include_path = tmp_path.joinpath("include.md")
    include_path.write_text("# Title")

    parser = RSTParser()
    document = make_document(parser_cls=RSTParser)
    parser.parse(
        f".. include:: {include_path}\n   :parser: myst_parser.docutils_", document
    )
    assert (
        document.pformat().strip()
        == dedent(
            """\
            <document source="notset">
                <section ids="title" names="title">
                    <title>
                        Title
            """
        ).strip()
    )


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        pytest.param(
            """\
            - manually numbered[^3]
            - auto numbered[^myref]

            [^myref]: auto definition.
            [^3]: manual definition.
            """,
            ["3", "myref"],
            id="manual-and-auto",
        ),
        pytest.param(
            """\
            - manually numbered[^3]
            - auto numbered[^x]

            [^x]:
            [^3]: three
            """,
            ["3", "x"],
            id="empty-auto-definition",
        ),
        pytest.param(
            """\
            - one[^first] two[^second] three[^3]

            [^first]: zebra
            [^second]: apple
            [^3]: three
            """,
            ["3", "first", "second"],
            id="unlabelled-not-sorted-by-text",
        ),
        pytest.param(
            """\
            - one[^second] two[^first] three[^3]

            [^first]: apple
            [^second]: zebra
            [^3]: three
            """,
            ["3", "second", "first"],
            id="unlabelled-keep-reference-order",
        ),
    ],
)
@pytest.mark.skipif(
    docutils_version < (0, 22),
    reason="docutils < 0.22 parses a :parser: include with the host's settings, "
    "without the MyST settings",
)
def test_include_from_rst_mixed_footnotes(tmp_path, source, expected):
    """Test the sort of footnotes in markdown included from an RST file (#1025).

    docutils' ``Footnotes`` transform does not run in the ``:parser:`` sub-document,
    so the auto-numbered footnotes have no label child when ``CollectFootnotes`` sorts:
    they must neither crash the sort (``TypeError`` against a numeric label,
    ``IndexError`` for an empty definition) nor be sorted by their body text,
    but keep the order they are first referenced (the order docutils numbers them).
    """
    from docutils.parsers.rst import Parser as RSTParser

    include_path = tmp_path.joinpath("include.md")
    include_path.write_text(dedent(source))

    parser = RSTParser()
    document = make_document(parser_cls=RSTParser)
    parser.parse(
        f".. include:: {include_path}\n   :parser: myst_parser.docutils_", document
    )
    document.transformer.populate_from_components([parser])
    document.transformer.apply_transforms()

    # labelled footnotes first, then the unlabelled ones in first-reference order
    assert [f["names"] for f in document.findall(nodes.footnote)] == [
        [name] for name in expected
    ]


def test_field_list_body_source_line():
    """A ``field_body`` node should carry its own source line.

    Regression: ``render_field_list`` previously stamped the line/source onto the
    ``field_name`` twice, leaving the ``field_body`` with no source mapping.
    """
    doctree = publish_doctree(
        source=":name: value\n",
        parser=Parser(),
        settings_overrides={"myst_enable_extensions": ["fieldlist"]},
    )
    bodies = list(doctree.findall(nodes.field_body))
    assert bodies, "expected a field_body node"
    assert bodies[0].line  # a real line, not 0/None


def test_linkify_disabled_without_linkify_it_py(monkeypatch):
    """Enabling ``linkify`` without ``linkify-it-py`` warns and disables it.

    Regression: previously the first parse crashed with
    ``ModuleNotFoundError("Linkify enabled but not installed.")``.
    """
    monkeypatch.setattr(markdown_it.main, "linkify_it", None)
    # the parser factory silently disables the extension (no crash on parse)
    md = create_md_parser(
        MdParserConfig(enable_extensions={"linkify"}), DocutilsRenderer
    )
    assert md.options["linkify"] is False
    md.parse("see https://example.com\n")
    # the docutils parser emits a suppressible myst warning
    stream = io.StringIO()
    publish_doctree(
        source="see https://example.com\n",
        parser=Parser(),
        settings_overrides={
            "myst_enable_extensions": ["linkify"],
            "warning_stream": stream,
        },
    )
    assert "[myst.linkify]" in stream.getvalue()
    stream = io.StringIO()
    publish_doctree(
        source="see https://example.com\n",
        parser=Parser(),
        settings_overrides={
            "myst_enable_extensions": ["linkify"],
            "myst_suppress_warnings": ["myst.linkify"],
            "warning_stream": stream,
        },
    )
    assert "[myst.linkify]" not in stream.getvalue()


@pytest.mark.skipif(
    importlib.util.find_spec("linkify_it") is None,
    reason="linkify-it-py not installed",
)
def test_linkify_no_warning_when_available():
    """No warning is emitted when ``linkify-it-py`` is installed."""
    stream = io.StringIO()
    publish_doctree(
        source="see https://example.com\n",
        parser=Parser(),
        settings_overrides={
            "myst_enable_extensions": ["linkify"],
            "warning_stream": stream,
        },
    )
    assert "[myst.linkify]" not in stream.getvalue()


def test_section_ref_resolution():
    """A ``§1`` reference resolves to an internal link to the numbered heading."""
    source = dedent(
        """\
        # Title

        See §1, §1.1 and §2.

        ## Section One

        ### Sub One One

        ## Section Two
        """
    )
    doctree = publish_doctree(
        source=source,
        parser=Parser(),
        settings_overrides={"myst_enable_extensions": ["section_ref"]},
    )
    refs = list(doctree.findall(nodes.reference))
    assert [(ref.astext(), ref["refid"], ref["reftitle"]) for ref in refs] == [
        ("§1", "section-one", "Section One"),
        ("§1.1", "sub-one-one", "Sub One One"),
        ("§2", "section-two", "Section Two"),
    ]
    assert all("section-ref" in ref["classes"] and ref["internal"] for ref in refs)


def test_section_ref_unresolved_warning():
    """An unresolvable ``§`` reference emits a suppressible ``myst.section_ref`` warning."""
    source = "# Title\n\nSee §9.9.\n\n## Only Section\n"
    stream = io.StringIO()
    doctree = publish_doctree(
        source=source,
        parser=Parser(),
        settings_overrides={
            "myst_enable_extensions": ["section_ref"],
            "warning_stream": stream,
        },
    )
    assert "[myst.section_ref]" in stream.getvalue()
    # the reference is left in place as styled inline text
    inlines = [
        node for node in doctree.findall(nodes.inline) if "section_numbers" in node
    ]
    assert [node.astext() for node in inlines] == ["§9.9"]

    # the warning is suppressible
    stream = io.StringIO()
    publish_doctree(
        source=source,
        parser=Parser(),
        settings_overrides={
            "myst_enable_extensions": ["section_ref"],
            "myst_suppress_warnings": ["myst.section_ref"],
            "warning_stream": stream,
        },
    )
    assert "[myst.section_ref]" not in stream.getvalue()


def test_section_ref_left_inert_in_link_and_heading():
    """A ``§`` reference inside link text or a heading stays inert styled text.

    Converting it would nest an ``<a>`` inside another ``<a>`` (link text) or
    inside toc/contents entry links (heading), so no reference is created and no
    warning is emitted for it, whether or not the number would resolve.
    """
    source = dedent(
        """\
        # Title

        ## Heading with §1 inside

        ## Other

        A link [see §1](https://example.com) and body §1.
        """
    )
    stream = io.StringIO()
    doctree = publish_doctree(
        source=source,
        parser=Parser(),
        settings_overrides={
            "myst_enable_extensions": ["section_ref"],
            "warning_stream": stream,
        },
    )
    # no reference is ever nested inside another reference
    for ref in doctree.findall(nodes.reference):
        assert not list(ref.findall(nodes.reference, include_self=False))
    # the heading ref and the in-link ref remain inert inline markers,
    # while the plain body ref resolves to the first section
    inert = [
        node for node in doctree.findall(nodes.inline) if "section_numbers" in node
    ]
    assert [node.astext() for node in inert] == ["§1", "§1"]
    resolved = [
        ref
        for ref in doctree.findall(nodes.reference)
        if "section-ref" in ref["classes"]
    ]
    assert [(r.astext(), r["refid"]) for r in resolved] == [
        ("§1", "heading-with-1-inside")
    ]
    # inert markers are skipped silently (no warning)
    assert "[myst.section_ref]" not in stream.getvalue()


def test_html_deep_nesting_warns():
    """Deeply nested HTML degrades to raw output with a warning.

    Regression: rendering the HTML AST recurses once per nesting level,
    and the resulting ``RecursionError`` escaped and aborted the build.
    """
    # rendering uses >=1 stack frame per nesting level, so this depth
    # always overflows, whatever the currently available stack
    depth = sys.getrecursionlimit()
    # tags on separate lines, to stay under docutils' line-length-limit
    source = (
        '<div class="admonition"><p class="title">Title</p>\n'
        + "<div>\n" * depth
        + "content\n"
        + "</div>\n" * depth
        + "</div>\n"
    )
    stream = io.StringIO()
    doctree = publish_doctree(
        source=source,
        parser=Parser(),
        settings_overrides={
            "myst_enable_extensions": ["html_admonition"],
            "warning_stream": stream,
        },
    )
    assert "HTML is too deeply nested" in stream.getvalue()
    assert "[myst.html]" in stream.getvalue()
    # the original text is preserved as a raw HTML node
    assert list(doctree.findall(nodes.raw))


@pytest.mark.parametrize(
    "yaml_line",
    [
        "title: !UnknownTag value",  # yaml.constructor.ConstructorError
        "date: 2021-99-99",  # bare ValueError from an out-of-range timestamp
    ],
)
def test_topmatter_hostile_yaml_warns(yaml_line):
    """Front matter YAML errors beyond parser/scanner ones warn, not crash.

    Regression: only ``ParserError``/``ScannerError`` were caught, so e.g. a
    ``ConstructorError`` from an unknown tag aborted the whole build.
    """
    stream = io.StringIO()
    doctree = publish_doctree(
        source=f"---\n{yaml_line}\n---\n\ncontent\n",
        parser=Parser(),
        settings_overrides={"warning_stream": stream},
    )
    assert "[myst.topmatter]" in stream.getvalue()
    assert "content" in doctree.pformat()


def test_footnote_label_matching_heading_name():
    """A footnote label sharing a heading's name is not a duplicate.

    Regression: the duplicate check used ``document.nameids``, which holds
    every target name, so the footnote definition was silently dropped.
    """
    stream = io.StringIO()
    doctree = publish_doctree(
        source="# Note\n\n[^note]\n\n[^note]: the definition\n",
        parser=Parser(),
        settings_overrides={"warning_stream": stream},
    )
    footnotes = list(doctree.findall(nodes.footnote))
    assert footnotes, "expected the footnote definition to be kept"
    assert "the definition" in footnotes[0].astext()
    assert "Duplicate footnote" not in stream.getvalue()


def test_footnote_label_matching_explicit_target():
    """A footnote label sharing an *explicit* target's name is dropped.

    Registering it would strip the name from both nodes and so break
    previously working references to the target, with confusing docutils
    warnings; the pre-existing drop-with-warning behaviour is kept.
    """
    stream = io.StringIO()
    doctree = publish_doctree(
        source="(note)=\n\ntext\n\n[^note]: the definition\n",
        parser=Parser(),
        settings_overrides={"warning_stream": stream},
    )
    assert "Duplicate footnote definition" in stream.getvalue()
    assert "Duplicate explicit target name" not in stream.getvalue()
    assert not list(doctree.findall(nodes.footnote))
    # the original target keeps its name, so references to it still resolve
    assert "note" in doctree.nameids
    assert doctree.nameids["note"]


@pytest.mark.parametrize(
    "source",
    [
        pytest.param("{#x}\n# First\n\n{#x}\n# Second\n", id="heading-heading"),
        pytest.param("{#x}\n# First\n\n(x)=\ntext\n", id="heading-target"),
        pytest.param("{#x}\n# First\n\n{#x}\nparagraph\n", id="heading-paragraph"),
        pytest.param("{#first}\n# First\n\n{#first}\n# Second\n", id="id-equals-title"),
    ],
)
def test_attrs_block_heading_duplicate_id_warns(source):
    """A heading ``{#id}`` that is later duplicated warns, rather than crashing.

    Regression: on docutils < 0.23 the heading's explicit name was registered a
    second time as an implicit one, so the node collided with itself and the
    duplicate aborted the build with ``ValueError: list.remove(x)``.
    This needs no Sphinx, so it also covers the docutils-only CI legs.
    """
    stream = io.StringIO()
    publish_doctree(
        source=source,
        parser=Parser(),
        settings_overrides={
            "myst_enable_extensions": ["attrs_block"],
            "warning_stream": stream,
        },
    )
    assert "Duplicate explicit target name" in stream.getvalue()


def test_topmatter_deeply_nested_yaml_warns():
    """Deeply nested front matter YAML warns instead of crashing.

    Regression: PyYAML's composer recurses per nesting level, and the
    resulting ``RecursionError`` is neither a ``YAMLError`` nor a
    ``ValueError``, so it escaped and aborted the build.

    The nesting must be a single-line flow sequence: spread over lines it
    fails in the (iterative) scanner instead, never reaching the composer.
    """
    # pin the limit so the depth both overflows it and, as a single line,
    # stays under docutils' line-length-limit (10000), whatever the runner
    depth = 1000
    limit = sys.getrecursionlimit()
    source = "---\nkey: " + "[" * depth + "]" * depth + "\n---\n\ncontent\n"
    stream = io.StringIO()
    try:
        sys.setrecursionlimit(depth)
        doctree = publish_doctree(
            source=source,
            parser=Parser(),
            settings_overrides={"warning_stream": stream},
        )
    finally:
        sys.setrecursionlimit(limit)
    assert "[myst.topmatter]" in stream.getvalue()
    assert "content" in doctree.pformat()


@pytest.mark.parametrize(
    "yaml_block",
    [
        "review:\n  date: 2026-08-03",  # date nested in a mapping
        "reviewed: [2026-08-03]",  # date nested in a sequence
        "review:\n  at: 2026-08-03T12:00:00",  # datetime nested in a mapping
    ],
)
def test_topmatter_nested_dates_do_not_crash(yaml_block):
    """YAML dates nested in dicts/lists must not abort the build.

    Top-level ``date``/``datetime`` scalars skip JSON encoding, but a nested
    date used to reach ``json.dumps`` and raise ``TypeError`` (#1203).
    """
    stream = io.StringIO()
    doctree = publish_doctree(
        source=f"---\n{yaml_block}\n---\n\ncontent\n",
        parser=Parser(),
        settings_overrides={"warning_stream": stream},
    )
    assert "content" in doctree.pformat()
    assert "2026-08-03" in doctree.astext()
    assert "[myst.topmatter]" not in stream.getvalue()


def test_topmatter_date_mapping_key_warns():
    """A YAML date used as a mapping *key* cannot be JSON-serialized.

    ``json.dumps``'s ``default=`` hook is not called for keys, so this still
    cannot be rendered as a field, but it must warn rather than crash,
    and only that field is dropped.
    """
    stream = io.StringIO()
    doctree = publish_doctree(
        source="---\nreview:\n  2026-08-03: done\nother: [2026-08-04]\n---\n\ncontent\n",
        parser=Parser(),
        settings_overrides={"warning_stream": stream},
    )
    assert "content" in doctree.pformat()
    assert "Front matter field 'review' could not be serialized" in stream.getvalue()
    assert "[myst.topmatter]" in stream.getvalue()
    assert _topmatter_fields(doctree) == {"other": '["2026-08-04"]'}


def _topmatter_fields(doctree: nodes.document) -> dict[str, str]:
    """Return the rendered front matter fields, as ``{name: body text}``."""
    return {
        field[0].astext(): field[1].astext() for field in doctree.findall(nodes.field)
    }


@pytest.mark.parametrize(
    ("yaml_block", "expected"),
    [
        pytest.param(
            "review:\n  at: 2026-08-03T12:00:00",
            '{"at": "2026-08-03T12:00:00"}',
            id="nested-datetime-isoformat",
        ),
        pytest.param(
            "review:\n  at: 2026-08-03T12:00:00+02:00",
            '{"at": "2026-08-03T12:00:00+02:00"}',
            id="nested-tz-datetime-isoformat",
        ),
        pytest.param(
            "tags: !!set {gamma, alpha, beta}",
            '["alpha", "beta", "gamma"]',
            id="set-sorted",
        ),
        pytest.param(
            "review:\n  d: !!set {2026-08-10, 2026-08-04, 2026-08-03}",
            '{"d": ["2026-08-03", "2026-08-04", "2026-08-10"]}',
            id="nested-set-of-dates",
        ),
        pytest.param(
            "tags: !!set {1, b, 2026-08-03}",
            '["2026-08-03", "b", 1]',
            id="mixed-type-set",
        ),
    ],
)
def test_topmatter_json_rendering(yaml_block, expected):
    """Values JSON has no type for render deterministically.

    Dates and datetimes nested in a mapping or list render as ISO 8601 strings,
    and a YAML ``!!set`` renders as a sorted list,
    so the output does not depend on hash randomization (``PYTHONHASHSEED``).
    """
    stream = io.StringIO()
    doctree = publish_doctree(
        source=f"---\n{yaml_block}\n---\n\ncontent\n",
        parser=Parser(),
        settings_overrides={"warning_stream": stream},
    )
    key = yaml_block.split(":", 1)[0]
    assert _topmatter_fields(doctree) == {key: expected}
    assert "[myst.topmatter]" not in stream.getvalue()


def test_topmatter_alias_expansion_bomb_warns():
    """A YAML alias-expansion ("billion laughs") bomb warns, not hangs.

    ``yaml.safe_load`` keeps aliased structures shared, so loading is cheap,
    but serializing the field for display would expand ``9**20`` items.
    """
    lines = ["a0: &a0 [x, x, x, x, x, x, x, x, x]"]
    for i in range(1, 20):
        refs = ", ".join([f"*a{i - 1}"] * 9)
        lines.append(f"a{i}: &a{i} [{refs}]")
    source = "---\n" + "\n".join(lines) + "\n---\n\ncontent\n"
    stream = io.StringIO()
    doctree = publish_doctree(
        source=source,
        parser=Parser(),
        settings_overrides={"warning_stream": stream},
    )
    assert "too large to render" in stream.getvalue()
    assert "[myst.topmatter]" in stream.getvalue()
    assert "content" in doctree.pformat()


def test_topmatter_set_alias_bomb_warns():
    """A ``!!set`` repeated through YAML aliases counts toward the size limit.

    Sets render as lists, so their items must be measured too;
    otherwise a few KB of front matter renders to tens of MB.
    Field ``c`` expands to about 20,000 items (rendered),
    field ``d`` to about 200,000 (over the limit, so it warns).
    """
    items = ", ".join(f"k{i}" for i in range(200))
    source = (
        f"---\na: &a !!set {{{items}}}\n"
        f"b: &b [{', '.join(['*a'] * 10)}]\n"
        f"c: &c [{', '.join(['*b'] * 10)}]\n"
        f"d: [{', '.join(['*c'] * 10)}]\n---\n\ncontent\n"
    )
    stream = io.StringIO()
    doctree = publish_doctree(
        source=source,
        parser=Parser(),
        settings_overrides={"warning_stream": stream},
    )
    assert "content" in doctree.pformat()
    warnings = stream.getvalue()
    assert "Front matter field 'd' is too large to render" in warnings
    assert "Front matter field 'c'" not in warnings


def test_heading_anchors_html_ids_disabled():
    """``myst_heading_anchors_html_ids=False`` restores lookup-only slugs."""
    settings: dict = {"myst_heading_anchors": 1, "doctitle_xform": False}
    doctree = publish_doctree(
        source="# Ubuntu 20.04\n", parser=Parser(), settings_overrides=settings
    )
    section = next(doctree.findall(nodes.section))
    assert section["ids"] == ["ubuntu-20-04", "ubuntu-2004"]
    doctree = publish_doctree(
        source="# Ubuntu 20.04\n",
        parser=Parser(),
        settings_overrides={**settings, "myst_heading_anchors_html_ids": False},
    )
    section = next(doctree.findall(nodes.section))
    assert section["ids"] == ["ubuntu-20-04"]
    assert section["slug"] == "ubuntu-2004"


def test_slug_id_cannot_steal_later_ids():
    """A heading's slug id must not claim an id another element receives.

    Regression: slugs were registered in ``document.ids`` at parse time,
    so docutils deduplicated *later* elements' ids around them, silently
    renaming previously published (or user-chosen) ids.
    """
    settings: dict = {"myst_heading_anchors": 1, "doctitle_xform": False}
    # the first heading's slug == the second heading's docutils id:
    # the second heading must keep its id, the colliding slug is skipped
    doctree = publish_doctree(
        source="# Ubuntu 20.04\n\n# Ubuntu 2004\n",
        parser=Parser(),
        settings_overrides=settings,
    )
    ids = [s["ids"] for s in doctree.findall(nodes.section)]
    assert ids == [["ubuntu-20-04"], ["ubuntu-2004", "ubuntu-2004-1"]]
    # the first heading's slug == a user's explicit target name:
    # the explicit target keeps its id
    doctree = publish_doctree(
        source="# Ubuntu 20.04\n\n(ubuntu-2004)=\n\n# Other\n",
        parser=Parser(),
        settings_overrides=settings,
    )
    ids = [s["ids"] for s in doctree.findall(nodes.section)]
    assert ids[0] == ["ubuntu-20-04"]
    assert ids[1][0] == "ubuntu-2004"
    assert "ubuntu-2004-1" not in ids[1]


def test_whitespace_slug_not_emitted_as_id():
    """A custom slug_func returning whitespace does not produce an HTML id."""
    doctree = publish_doctree(
        source="# ab cd\n",
        parser=Parser(),
        settings_overrides={
            "myst_heading_anchors": 1,
            "doctitle_xform": False,
            # reverses the title, producing "dc ba" (contains a space)
            "myst_heading_slug_func": "myst_parser.config.main._test_slug_func",
        },
    )
    section = next(doctree.findall(nodes.section))
    assert section["slug"] == "dc ba"
    assert section["ids"] == ["ab-cd"]


def test_heading_slug_func_unknown_preset():
    """An unknown ``heading_slug_func`` string errors, naming the presets."""
    from myst_parser.config.main import MdParserConfig

    with pytest.raises(TypeError, match="github, gitlab"):
        MdParserConfig(heading_slug_func="bogus")


def test_footnote_duplicate_definition_warns():
    """A genuinely duplicated footnote definition still warns and is dropped."""
    stream = io.StringIO()
    doctree = publish_doctree(
        source="[^a]\n\n[^a]: first\n\n[^a]: second\n",
        parser=Parser(),
        settings_overrides={"warning_stream": stream},
    )
    assert "Duplicate footnote definition" in stream.getvalue()
    assert len(list(doctree.findall(nodes.footnote))) == 1


def test_directive_block_text_rst_parity():
    """A fenced directive's ``self.block_text`` mirrors the rST full source.

    The block text spans the opening fence, options block, body and closing
    fence, while ``self.content``/``self.content_offset`` stay body-relative.
    """
    from docutils.parsers.rst import Directive
    from docutils.parsers.rst import directives as rst_directives

    captured = {}

    class _BlockTextEcho(Directive):
        has_content = True
        option_spec = {"class": rst_directives.class_option}

        def run(self):
            captured["block_text"] = self.block_text
            captured["content"] = list(self.content)
            captured["content_offset"] = self.content_offset
            return []

    rst_directives.register_directive("blocktextecho", _BlockTextEcho)
    try:
        publish_doctree(
            source="```{blocktextecho}\n---\nclass: tip\n---\nbody line\n```\n",
            parser=Parser(),
            settings_overrides={"warning_stream": io.StringIO()},
        )
    finally:
        rst_directives._directives.pop("blocktextecho", None)
    assert captured["block_text"] == (
        "```{blocktextecho}\n---\nclass: tip\n---\nbody line\n```\n"
    )
    assert captured["content"] == ["body line"]
    assert captured["content_offset"] == 3


def test_directive_block_text_fallback():
    """Directives run from synthesized (non-source) content, such as HTML
    admonitions, receive that content as ``block_text``."""
    from docutils.parsers.rst import Directive
    from docutils.parsers.rst import directives as rst_directives

    captured = {}

    class _Echo(Directive):
        required_arguments = 1
        final_argument_whitespace = True
        has_content = True
        option_spec = {"class": rst_directives.class_option}

        def run(self):
            captured["block_text"] = self.block_text
            return []

    rst_directives.register_directive("admonition", _Echo)
    try:
        publish_doctree(
            source='<div class="admonition">\nTitle text\n\nBody text here\n</div>\n',
            parser=Parser(),
            settings_overrides={
                "warning_stream": io.StringIO(),
                "myst_enable_extensions": ["html_admonition"],
            },
        )
    finally:
        rst_directives._directives.pop("admonition", None)
    assert captured["block_text"] == ":class: admonition\n\nTitle text\n"


def test_html_image_option_warning_line():
    """Option warnings for HTML-synthesized directives point at the element.

    The synthesized ``:key: value`` content has no source lines, so warnings
    must fall back to the element's own line, not per-key arithmetic.
    """
    stream = io.StringIO()
    publish_doctree(
        source="para\n\npara two\n\n<img src='x.png' width='not!valid'>\n",
        parser=Parser(),
        settings_overrides={
            "warning_stream": stream,
            "myst_enable_extensions": ["html_image"],
        },
    )
    assert "<string>:5: (WARNING/2) 'image': Invalid option value for 'width'" in (
        stream.getvalue()
    )


def test_colon_fence_option_warning_line():
    """Per-key option warning lines also apply to ``:::`` fence directives."""
    stream = io.StringIO()
    publish_doctree(
        source="para\n\n:::{note}\n:foo: bar\nbody\n:::\n",
        parser=Parser(),
        settings_overrides={
            "warning_stream": stream,
            "myst_enable_extensions": ["colon_fence"],
        },
    )
    assert "<string>:4: (WARNING/2) 'note': Unknown option key: 'foo'" in (
        stream.getvalue()
    )


def test_include_literal_line(tmp_path):
    """A literal ``include`` block's source line reflects ``start-line``."""
    inc = tmp_path / "inc.txt"
    inc.write_text("l1\nl2\nl3\nl4\nl5\n")
    source_path = str(tmp_path / "main.md")

    doctree = publish_doctree(
        source=f"```{{include}} {inc}\n:literal: true\n:start-line: 2\n```\n",
        source_path=source_path,
        parser=Parser(),
        settings_overrides={"warning_stream": io.StringIO()},
    )
    literal_block = next(doctree.findall(nodes.literal_block))
    assert literal_block.line == 3
    assert literal_block.astext() == "l3\nl4\nl5"

    doctree = publish_doctree(
        source=f"```{{include}} {inc}\n:literal: true\n```\n",
        source_path=source_path,
        parser=Parser(),
        settings_overrides={"warning_stream": io.StringIO()},
    )
    literal_block = next(doctree.findall(nodes.literal_block))
    assert literal_block.line == 1


def test_text_node_line_stamping():
    """Text nodes carry their enclosing block's line, not a stale one.

    Regression for a directive's line being stamped
    (via ``document.current_line`` and docutils' ``Node.setup_child``)
    onto every subsequent ``Text`` node in the document.
    """
    source = (
        "para one\n\n```{note}\n:class: tip\n\nnote body\n```\n\npara two\n\n- item\n"
    )
    doctree = publish_doctree(
        source=source,
        parser=Parser(),
        settings_overrides={"warning_stream": io.StringIO()},
    )
    lines = {text.astext(): text.line for text in doctree.findall(nodes.Text)}
    assert lines["para one"] == 1
    # previously stamped with the note directive's line (3)
    assert lines["para two"] == 9
    assert lines["item"] == 11
    # created while detached from the document, so defers to ancestor lookup
    assert lines["note body"] is None


@pytest.mark.parametrize(
    ("options", "lines"),
    [
        pytest.param(":class: tip\n", [3, 5], id="colon"),
        pytest.param("---\nclass: tip\n---\n", [5, 7], id="yaml"),
        # text after the closing `---` is the first body line (#1164)
        pytest.param("---\nclass: tip\n--- ", [4, 6], id="yaml-closer-text"),
    ],
)
def test_directive_body_lines_with_options_and_trailing_blank(options, lines):
    """Body elements and their warnings map to their true source lines.

    Regression for #1177: with an options block and a blank line before the
    closing fence, every body line was mapped one source line too low.
    """
    source = f"```{{note}}\n{options}para {{unknownrole}}`x`\n\npara2\n\n```\n"
    stream = io.StringIO()
    doctree = publish_doctree(
        source=source,
        parser=Parser(),
        settings_overrides={"warning_stream": stream},
    )
    note = next(doctree.findall(nodes.note))
    assert [c.line for c in note.children if isinstance(c, nodes.paragraph)] == lines
    assert f"<string>:{lines[0]}: (WARNING/2) Unknown interpreted text role" in (
        stream.getvalue()
    )


def test_empty_slug_means_no_anchor():
    """A heading whose title slugifies to nothing gets no anchor.

    In particular the empty slug takes no part in deduplication, so a later
    empty-slugging heading must not receive a nonsense ``-1`` anchor id.
    """
    doctree = publish_doctree(
        source="# !!!\n\n# ???\n",
        parser=Parser(),
        settings_overrides={
            "warning_stream": io.StringIO(),
            "doctitle_xform": False,
            "myst_heading_anchors": 2,
        },
    )
    for section in doctree.findall(nodes.section):
        assert "slug" not in section.attributes, section.attributes
        assert section["ids"] and all(not i.startswith("-") for i in section["ids"]), (
            section["ids"]
        )


def test_docutils_slug_preset():
    """The ``docutils`` preset produces make_id-style anchors.

    Non-Latin titles slugify to nothing under this preset, so those headings
    get no anchor.
    """
    doctree = publish_doctree(
        source="# Привет\n\n# 2.0\n\n# Hello World\n\n# Straße & Œuvre\n",
        parser=Parser(),
        settings_overrides={
            "warning_stream": io.StringIO(),
            "doctitle_xform": False,
            "myst_heading_anchors": 2,
            "myst_heading_slug_func": "docutils",
        },
    )
    slugs = [section.get("slug") for section in doctree.findall(nodes.section)]
    assert slugs == [None, None, "hello-world", "strasze-oeuvre"]


def test_definition_list_orphan_definition():
    """A definition with no preceding term errors, but keeps its content.

    Not reachable via the deflist plugin (which never emits an orphan ``dd``),
    so constructed as a synthetic token stream.
    """
    md = create_md_parser(
        MdParserConfig(enable_extensions={"deflist"}), DocutilsRenderer
    )
    tokens = [
        Token("dl_open", "dl", 1, map=[0, 2]),
        Token("dd_open", "dd", 1, map=[0, 1]),
        Token("paragraph_open", "p", 1, map=[0, 1]),
        Token(
            "inline",
            "",
            0,
            content="important content",
            map=[0, 1],
            children=[Token("text", "", 0, content="important content")],
        ),
        Token("paragraph_close", "p", -1),
        Token("dd_close", "dd", -1),
        Token("dl_close", "dl", -1),
    ]
    document = make_document("source.md")
    md.options["document"] = document
    md.renderer.render(tokens, md.options, {})
    output = document.pformat()
    assert "no preceding term" in output
    assert "important content" in output


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        pytest.param("$$\na = 1\n$$", "a = 1", id="newlines"),
        pytest.param("$$\n\na = 1\n\n$$", "a = 1", id="blank-lines"),
        pytest.param("$$\n  \na = 1\n  \n$$", "a = 1", id="whitespace-lines"),
        pytest.param("$$\na = 1\n$$ (label)", "a = 1", id="label"),
        pytest.param("$$\n\na = 1\n\n$$ (label)", "a = 1", id="label-blank-lines"),
        pytest.param("$$\na = 1\n\nb = 2\n$$", "a = 1\n\nb = 2", id="interior-kept"),
        pytest.param("$$\n  a\n    b\n$$", "  a\n    b", id="indentation-kept"),
        pytest.param("$$ a = 1 $$", " a = 1 ", id="single-line-unchanged"),
    ],
)
def test_math_block_blank_boundary_lines(source, expected):
    """``$$`` math block content has no leading or trailing blank lines.

    Like the rST ``math`` directive, only whole blank lines at the start and
    end are removed (#614).
    """
    doctree = publish_doctree(
        source=source,
        parser=Parser(),
        settings_overrides={
            "warning_stream": io.StringIO(),
            "myst_enable_extensions": ["dollarmath"],
        },
    )
    blocks = list(doctree.findall(nodes.math_block))
    assert [block.astext() for block in blocks] == [expected]


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        pytest.param("Some text\n$$\na = 1\n$$\nmore text.", "a = 1", id="newlines"),
        pytest.param(
            "Some text\n$$  \na = 1\n  $$\nmore text.",
            "a = 1",
            id="whitespace-lines",
        ),
        pytest.param("text $$ a = 1 $$ text", " a = 1 ", id="single-line-unchanged"),
    ],
)
def test_math_inline_double_blank_boundary_lines(source, expected):
    """``$$`` inside a paragraph has no leading or trailing blank lines.

    With ``myst_dmath_double_inline``, such a ``$$`` pair is rendered as a
    ``math_block`` too, so its content is trimmed the same way (#614).
    """
    doctree = publish_doctree(
        source=source,
        parser=Parser(),
        settings_overrides={
            "warning_stream": io.StringIO(),
            "myst_enable_extensions": ["dollarmath"],
            "myst_dmath_double_inline": True,
        },
    )
    blocks = list(doctree.findall(nodes.math_block))
    assert [block.astext() for block in blocks] == [expected]


def assert_no_blank_line_in_math_env(output: str) -> None:
    """Assert no display math environment in ``output`` has a blank line.

    This checks the property itself, independent of which environment
    the docutils LaTeX writer picks or how it lays out the lines.
    """
    bodies = re.findall(
        r"\\begin\{(equation\*|align\*)\}(.*?)\\end\{\1\}", output, re.DOTALL
    )
    assert bodies, output
    for _, body in bodies:
        assert re.search(r"\n[ \t]*\n", body) is None, body


def test_math_block_latex_no_blank_lines():
    """The LaTeX writer output has no blank line inside a math environment.

    A blank line there ends the paragraph, and pdflatex fails with
    "Paragraph ended before \\align* was complete" (#614).
    The source is the example from the issue.
    """
    source = dedent(
        r"""
        $$
        n & = & 41*23 = 943 \\
        (p-1)(q-1) & = & 40*22 = 880 \\
        e & = & 753
        $$

        $$
           \begin{eqnarray}
              y    & = & ax^2 + bx + c \\
              f(x) & = & x^2 + 2xy + y^2
           \end{eqnarray}
        $$
        """
    )
    output = publish_string(
        source=source,
        parser=Parser(),
        writer=LatexWriter(),
        settings_overrides={
            "output_encoding": "unicode",
            "warning_stream": io.StringIO(),
            "myst_enable_extensions": ["dollarmath"],
        },
    )
    assert "\\begin{align*}\nn & = & 41*23 = 943" in output
    assert "e & = & 753\n\\end{align*}" in output
    assert "\\begin{equation*}\n   \\begin{eqnarray}" in output
    assert "\\end{eqnarray}\n\\end{equation*}" in output
    assert_no_blank_line_in_math_env(output)


def test_math_inline_double_latex_no_blank_lines():
    """The LaTeX writer output has no blank line inside a math environment,
    for a ``$$`` pair inside a paragraph with ``myst_dmath_double_inline`` (#614).
    """
    source = "Some text\n$$\nn & = 943 \\\\\ne & = 753\n$$\nmore text.\n"
    output = publish_string(
        source=source,
        parser=Parser(),
        writer=LatexWriter(),
        settings_overrides={
            "output_encoding": "unicode",
            "warning_stream": io.StringIO(),
            "myst_enable_extensions": ["dollarmath"],
            "myst_dmath_double_inline": True,
        },
    )
    assert "\\begin{align*}" in output
    assert_no_blank_line_in_math_env(output)


@pytest.mark.parametrize(
    ("language_code", "smart_quotes", "locales", "expected"),
    [
        pytest.param(None, False, None, DEFAULT_SMARTQUOTES, id="unset"),
        pytest.param("", False, None, DEFAULT_SMARTQUOTES, id="empty"),
        pytest.param("   ", False, None, DEFAULT_SMARTQUOTES, id="whitespace"),
        pytest.param("en", False, None, DEFAULT_SMARTQUOTES, id="english"),
        pytest.param(
            "fr",
            False,
            None,
            ("\u00ab\u00a0", "\u00a0\u00bb", "\u201c", "\u201d"),
            id="french",
        ),
        pytest.param(
            "fr",
            "alt",
            None,
            ("\u00ab\u202f", "\u202f\u00bb", "\u201c", "\u201d"),
            id="french-alt",
        ),
        pytest.param(
            "fr-x-altquot",
            "alt",
            None,
            ("\u00ab\u00a0", "\u00a0\u00bb", "\u201c", "\u201d"),
            id="french-alt-toggle",
        ),
        pytest.param(
            "fr_CH",
            False,
            None,
            ("\u00ab", "\u00bb", "\u2039", "\u203a"),
            id="swiss-french",
        ),
        pytest.param(
            "de_AT",
            False,
            None,
            ("\u201e", "\u201c", "\u201a", "\u2018"),
            id="austrian-german-fallback",
        ),
        pytest.param(
            "zh_TW",
            False,
            None,
            ("\u300c", "\u300d", "\u300e", "\u300f"),
            id="traditional-chinese",
        ),
        pytest.param(
            "tlh",
            False,
            None,
            DEFAULT_SMARTQUOTES,
            id="unsupported-fallback",
        ),
        pytest.param(
            "fr_FR",
            False,
            [("fr_FR", ("<<", ">>", "<", ">")), ("", "abcd"), ("de", "bad")],
            ("<<", ">>", "<", ">"),
            id="custom-locale-override",
        ),
    ],
)
def test_resolve_smartquotes(language_code, smart_quotes, locales, expected):
    """``resolve_smartquotes`` honors Docutils locale rules without mutating globals (#806)."""
    from docutils.utils.smartquotes import smartchars

    snapshot = dict(smartchars.quotes)
    assert (
        resolve_smartquotes(
            language_code,
            smart_quotes=smart_quotes,
            smartquotes_locales=locales,
        )
        == expected
    )
    assert smartchars.quotes == snapshot


def test_create_md_parser_invalid_quotes():
    """``create_md_parser`` rejects quote overrides that do not specify 4 entries."""
    with pytest.raises(ValueError, match="exactly 4 quote strings"):
        create_md_parser(
            MdParserConfig(enable_extensions={"smartquotes"}),
            DocutilsRenderer,
            quotes=("<<", ">>"),
        )


@pytest.mark.parametrize(
    ("source", "settings", "expected"),
    [
        pytest.param(
            'Test\'s "double" and \'single\' and "*emph*"',
            {
                "language_code": "fr",
                "myst_enable_extensions": ["smartquotes"],
            },
            "Test\u2019s \u00ab\u00a0double\u00a0\u00bb and \u201csingle\u201d and \u00ab\u00a0emph\u00a0\u00bb",
            id="fr-default",
        ),
        pytest.param(
            '"Test"',
            {
                "language_code": "fr",
                "smart_quotes": "alt",
                "myst_enable_extensions": ["smartquotes"],
            },
            "\u00ab\u202fTest\u202f\u00bb",
            id="fr-alt",
        ),
        pytest.param(
            "---\nmyst:\n  enable_extensions: [smartquotes]\n---\n\"Hallo\" und 'Welt'",
            {
                "language_code": "de",
            },
            "\u201eHallo\u201c und \u201aWelt\u2018",
            id="de-topmatter",
        ),
        pytest.param(
            "\"Custom\" and 'quote'",
            {
                "language_code": "de",
                "smartquotes_locales": [("de", ("[", "]", "{", "}"))],
                "myst_enable_extensions": ["smartquotes"],
            },
            "[Custom] and {quote}",
            id="custom-locales",
        ),
    ],
)
def test_docutils_smartquotes_localized(source, settings, expected):
    """Docutils ``Parser`` localizes MyST ``smartquotes`` using document settings (#806)."""
    doctree = publish_doctree(
        source=source,
        parser=Parser(),
        settings_overrides={
            "warning_stream": io.StringIO(),
            **settings,
        },
    )
    assert doctree.astext() == expected
