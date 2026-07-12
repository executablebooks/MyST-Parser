import contextlib
import io
from dataclasses import dataclass, field, fields
from textwrap import dedent
from typing import Literal

from myst_parser.mdit_to_docutils.base import make_document
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
    from docutils import nodes
    from docutils.core import publish_doctree

    doctree = publish_doctree(
        source=":name: value\n",
        parser=Parser(),
        settings_overrides={"myst_enable_extensions": ["fieldlist"]},
    )
    bodies = list(doctree.findall(nodes.field_body))
    assert bodies, "expected a field_body node"
    field_name = bodies[0].parent[0]
    assert bodies[0].line == field_name.line
    assert bodies[0].line  # a real line, not 0/None


def test_linkify_requires_linkify_it_py(monkeypatch):
    """Enabling ``linkify`` without ``linkify-it-py`` raises a clear error.

    Regression: previously the parse would fail later with an opaque
    ``AttributeError`` on ``None``.
    """
    import markdown_it.main
    import pytest

    from myst_parser.config.main import MdParserConfig
    from myst_parser.mdit_to_docutils.base import DocutilsRenderer
    from myst_parser.parsers.mdit import create_md_parser

    monkeypatch.setattr(markdown_it.main, "linkify_it", None)
    with pytest.raises(ImportError, match="linkify-it-py"):
        create_md_parser(
            MdParserConfig(enable_extensions={"linkify"}), DocutilsRenderer
        )
