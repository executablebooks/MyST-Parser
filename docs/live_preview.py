import traceback
from io import StringIO

import yaml
from docutils.core import publish_string
from js import document

from myst_parser import __version__
from myst_parser.parsers.docutils_ import Parser


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
        }
    )
    try:
        output = publish_string(
            input_myst,
            parser=Parser(),
            writer_name=writer_name,
            settings_overrides=settings,
        )
    except Exception as exc:
        output = f"ERROR: conversion:\n{exc}\n{traceback.format_exc()}"
    return {"output": output, "warnings": warning_stream.getvalue()}


version_label = document.querySelector("span#myst-version")
config_textarea = document.querySelector("textarea#input_config")
input_textarea = document.querySelector("textarea#input_myst")
output_iframe = document.querySelector("iframe#output_html")
output_raw = document.querySelector("textarea#output_raw")
warnings_textarea = document.querySelector("textarea#output_warnings")
oformat_select = document.querySelector("select#output_format")


def do_convert(event=None):
    result = convert(config_textarea.value, input_textarea.value, oformat_select.value)
    output_raw.value = result["output"]
    if "html" in oformat_select.value:
        output_iframe.contentDocument.body.innerHTML = result["output"]
    else:
        output_iframe.contentDocument.body.innerHTML = (
            "Change output format to HTML to see output"
        )
    warnings_textarea.value = result["warnings"]


version_label.textContent = f"myst-parser v{__version__}"
config_textarea.oninput = do_convert
input_textarea.oninput = do_convert
oformat_select.onchange = do_convert

do_convert()
