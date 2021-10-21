import os

import pytest
from sphinx.application import Sphinx
from sphinx.errors import SphinxWarning

from myst_parser.main import MdParserConfig
from myst_parser.sphinx_parser import parse
from myst_parser.sphinx_renderer import mock_sphinx_env


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
        ("ref_colon", "(ref:colon)=\n# Title\n[](ref:colon)", False),
    ],
)
def test_parse(test_name, text, should_warn, file_regression):

    with mock_sphinx_env(
        conf={"extensions": ["myst_parser"]},
        srcdir="root",
        with_builder=True,
        raise_on_warning=True,
    ) as app:  # type: Sphinx
        app.env.myst_config = MdParserConfig()
        document = parse(app, text, docname="index")
        if should_warn:
            with pytest.raises(SphinxWarning):
                app.env.apply_post_transforms(document, "index")
        else:
            app.env.apply_post_transforms(document, "index")

    content = document.pformat()
    # windows fix
    content = content.replace("root" + os.sep + "index.md", "root/index.md")

    file_regression.check(content, basename=test_name, extension=".xml")
