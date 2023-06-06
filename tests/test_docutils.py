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
    from docutils.frontend import OptionParser

    stream = io.StringIO()
    OptionParser(components=(Parser,)).print_help(stream)
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
