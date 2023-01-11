from io import StringIO

import yaml
from docutils.core import publish_string
from js import document

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
    output = publish_string(
        input_myst,
        parser=Parser(),
        writer_name=writer_name,
        settings_overrides=settings,
    )
    return {"output": output, "warnings": warning_stream.getvalue()}


config_textarea = document.querySelector("textarea#input_config")
input_textarea = document.querySelector("textarea#input_myst")
output_textarea = document.querySelector("textarea#output_render")
warnings_textarea = document.querySelector("textarea#output_warnings")
oformat_select = document.querySelector("select#output_format")


def do_convert(event=None):
    result = convert(config_textarea.value, input_textarea.value, oformat_select.value)
    output_textarea.value = result["output"]
    warnings_textarea.value = result["warnings"]


config_textarea.oninput = do_convert
input_textarea.oninput = do_convert
oformat_select.onchange = do_convert

do_convert()
