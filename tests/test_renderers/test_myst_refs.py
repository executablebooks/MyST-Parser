from sphinx.application import Sphinx
from sphinx.errors import SphinxWarning

from myst_parser.sphinx_renderer import mock_sphinx_env
from myst_parser.sphinx_parser import parse

import pytest


@pytest.mark.parametrize(
    "test_name,text,should_warn",
    [
        ("null", "", False),
        ("missing", "[](ref)", True),
        ("doc", "[](index)", False),
        ("doc_with_extension", "[](index.md)", False),
        ("doc_nested", "[*text*](index)", False),
        ("ref", "(ref)=\n# Title\n[](ref)", False),
        ("ref_nested", "(ref)=\n# Title\n[*text*](ref)", False),
        ("duplicate", "(index)=\n# Title\n[](index)", True),
    ],
)
def test_parse(test_name, text, should_warn, file_regression):

    with mock_sphinx_env(
        conf={"extensions": ["myst_parser"]},
        srcdir="root",
        with_builder=True,
        raise_on_warning=True,
    ) as app:  # type: Sphinx
        document = parse(app, text, docname="index")
        if should_warn:
            with pytest.raises(SphinxWarning):
                app.env.apply_post_transforms(document, "index")
        else:
            app.env.apply_post_transforms(document, "index")

    file_regression.check(document.pformat(), basename=test_name, extension=".xml")
