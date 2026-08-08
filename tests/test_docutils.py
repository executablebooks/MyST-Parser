import contextlib
import importlib.util
import io
import sys
from dataclasses import dataclass, field, fields
from pathlib import Path
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


def test_include_source_line_attribution(tmp_path):
    """Warnings inside an ``{include}``\\ d file report the exact source line.

    Regression: every line was attributed one too low (``startline + 1``
    double-counted with the renderer's 0-based to 1-based conversion), and
    ``start-after`` advanced the line offset by *characters*.
    """

    def role_warning_location(main_source: str) -> str:
        stream = io.StringIO()
        publish_doctree(
            main_source,
            parser=Parser(),
            source_path=str(tmp_path / "main.md"),
            settings_overrides={"warning_stream": stream},
        )
        warnings_ = [
            line for line in stream.getvalue().splitlines() if "unknownrole" in line
        ]
        assert len(warnings_) == 1, stream.getvalue()
        # `path:line:` prefix of the docutils warning
        path, line, _ = warnings_[0].split(":", 2)
        return f"{Path(path).name}:{line}"

    inc = tmp_path / "inc.md"
    inc.write_text("line one\n\n{unknownrole}`x`\n")
    assert role_warning_location(f"```{{include}} {inc}\n```\n") == "inc.md:3"

    inc2 = tmp_path / "inc2.md"
    inc2.write_text("skip1\nskip2\npara\n\n{unknownrole}`y`\n")
    assert (
        role_warning_location(f"```{{include}} {inc2}\n:start-line: 2\n```\n")
        == "inc2.md:5"
    )

    inc3 = tmp_path / "inc3.md"
    inc3.write_text("intro\n<!-- start -->\n\n{unknownrole}`z`\n")
    assert (
        role_warning_location(
            f"```{{include}} {inc3}\n:start-after: <!-- start -->\n```\n"
        )
        == "inc3.md:4"
    )

    # nested includes: the innermost file's own lines
    b = tmp_path / "b.md"
    b.write_text("first\n\n{unknownrole}`b`\n")
    a = tmp_path / "a.md"
    a.write_text(f"a para\n\n```{{include}} {b}\n```\n")
    assert role_warning_location(f"```{{include}} {a}\n```\n") == "b.md:3"


def test_topmatter_global_only_and_validated_values():
    """Topmatter: global-only fields warn and are ignored; converting
    validators' values survive the merge.

    Regression: ``merge_file_level`` re-assigned the raw topmatter value over
    the value a converting validator had set, so e.g. a
    ``heading_slug_func`` preset name crashed at each heading
    (``'str' object is not callable``).
    """
    from myst_parser.config.main import MdParserConfig, merge_file_level

    warnings_: list[str] = []
    config = merge_file_level(
        MdParserConfig(),
        {
            "myst": {
                "heading_slug_func": "github",  # global-only
                "enable_extensions": ["colon_fence"],  # converting validator
                "title_to_header": True,  # plain local field
            }
        },
        lambda _, msg: warnings_.append(msg),
    )
    assert warnings_ == [
        "'heading_slug_func' is only allowed at the global level, ignoring"
    ]
    assert config.heading_slug_func is None
    assert config.enable_extensions == {"colon_fence"}
    assert isinstance(config.enable_extensions, set)
    assert config.title_to_header is True

    # end-to-end: no per-heading crash, a single topmatter warning
    stream = io.StringIO()
    publish_doctree(
        source="---\nmyst:\n  heading_slug_func: github\n---\n\n# Hello World\n",
        parser=Parser(),
        settings_overrides={"warning_stream": stream},
    )
    output = stream.getvalue()
    assert "is not callable" not in output
    assert "[myst.topmatter]" in output


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
