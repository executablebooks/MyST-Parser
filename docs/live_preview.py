import traceback
from io import StringIO

import yaml
from docutils.core import publish_string
from docutils.frontend import filter_settings_spec
from docutils.writers.html5_polyglot import HTMLTranslator, Writer
from js import document

from myst_parser import __version__
from myst_parser.parsers.docutils_ import Parser


class SimpleTranslator(HTMLTranslator):
    def visit_literal_block(self, node):
        node["classes"].append("highlight")
        return super().visit_literal_block(node)

    def stylesheet_call(self, *args, **kwargs):
        return ""


class SimpleWriter(Writer):
    settings_spec = filter_settings_spec(
        Writer.settings_spec,
        "template",
    )

    def apply_template(self):
        subs = self.interpolation_dict()
        return "%(body)s\n" % subs

    def __init__(self):
        self.parts = {}
        self.translator_class = SimpleTranslator


def convert(input_config: str, input_myst: str, writer_name: str) -> dict:
    warning_stream = StringIO()
    try:
        settings = yaml.safe_load(input_config) if input_config else {}
        assert isinstance(settings, dict), "not a dictionary"
    except Exception as exc:
        warning_stream.write(f"ERROR: config load: {exc}\n")
        settings = {}
    settings.update(
        {
            "output_encoding": "unicode",
            "warning_stream": warning_stream,
            # to mimic the sphinx parser
            "doctitle_xform": False,
            "sectsubtitle_xform": False,
            "initial_header_level": 1,
        }
    )
    try:
        output = publish_string(
            input_myst,
            parser=Parser(),
            settings_overrides=settings,
            **(
                {"writer": SimpleWriter()}
                if "html" in writer_name
                else {"writer_name": writer_name}
            ),
        )
    except Exception as exc:
        output = f"ERROR: conversion:\n{exc}\n{traceback.format_exc()}"
    return {"output": output, "warnings": warning_stream.getvalue()}


version_label = document.querySelector("span#myst-version")
config_textarea = document.querySelector("textarea#input_config")
input_textarea = document.querySelector("textarea#input_myst")
output_iframe = document.querySelector("div#output_html")
output_raw = document.querySelector("textarea#output_raw")
warnings_textarea = document.querySelector("textarea#output_warnings")
oformat_select = document.querySelector("select#output_format")


def do_convert(event=None):
    result = convert(config_textarea.value, input_textarea.value, oformat_select.value)
    output_raw.value = result["output"]
    if "html" in oformat_select.value:
        output_iframe.innerHTML = result["output"]
    else:
        output_iframe.innerHTML = "Change output format to HTML to see output"
    warnings_textarea.value = result["warnings"]


version_label.textContent = f"myst-parser v{__version__}"
config_textarea.oninput = do_convert
input_textarea.oninput = do_convert
oformat_select.onchange = do_convert

do_convert()
