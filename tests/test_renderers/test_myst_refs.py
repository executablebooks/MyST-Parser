from sphinx.application import Sphinx

from myst_parser.sphinx_renderer import mock_sphinx_env
from myst_parser.myst_refs import MystReferenceReslover
from myst_parser.sphinx_parser import parse

import pytest


@pytest.mark.parametrize(
    "test_name,text",
    [
        ("null", ""),
        ("missing", "[](ref)"),
        ("doc", "[](index)"),
        ("doc_with_extension", "[](index.md)"),
        ("doc_nested", "[*text*](index)"),
        ("ref", "(ref)=\n# Title\n[](ref)"),
        ("ref_nested", "(ref)=\n# Title\n[*text*](ref)"),
        ("duplicate", "(index)=\n# Title\n[](index)"),
    ],
)
def test_parse(test_name, text, caplog, data_regression):

    with mock_sphinx_env(srcdir="root", with_builder=True) as app:  # type: Sphinx
        app.add_post_transform(MystReferenceReslover)
        app.add_source_suffix(".md", "markdown")
        document = parse(app, text, docname="index")
        app.env.apply_post_transforms(document, "index")

    data_regression.check(
        {"doc": document.pformat(), "logs": caplog.record_tuples}, basename=test_name
    )
