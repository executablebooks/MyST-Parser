import contextlib
import importlib.util
import io
import sys
from dataclasses import dataclass, field, fields
from textwrap import dedent
from typing import Literal

import markdown_it.main
import pytest
from docutils import nodes
from docutils.core import publish_doctree
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
from myst_parser.parsers.mdit import create_md_parser


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
