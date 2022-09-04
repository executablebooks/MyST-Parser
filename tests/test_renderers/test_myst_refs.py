from pathlib import Path

import pytest
from sphinx.util import console
from sphinx_pytest.plugin import CreateDoctree

STATIC = Path(__file__).parent.absolute() / ".." / "static"

PARAMS = [
    ("null", "", None),
    (
        "unhandled",
        "[](ref)",
        "<src>/index.md:1: WARNING: Unhandled link URI (prepend with '#' or 'myst:project#'?): 'ref' [myst.link_uri]",  # noqa: E501
    ),
    ("doc", "[](index.md)", None),
    ("doc_text", "[*text*](index.md)", None),
    ("file", "[](other.txt)", None),
    ("file_text", "[*text*](other.txt)", None),
    ("local_anchor", "(ref)=\n# Title\n[](#ref)", None),
    ("local_anchor_text", "(ref)=\n# Title\n[*text*](#ref)", None),
    ("myst_project", "[](myst:project#index)", None),
    ("myst_project_text", "[*text*](myst:project#index)", None),
    (
        "myst_project_missing",
        "[*text*](myst:project#xxx)",
        "<src>/index.md:1: WARNING: Unmatched target 'local:?:?:xxx' [myst.xref_missing]",
    ),
    (
        "myst_project_duplicate",
        "(index)=\n# Title\n[text](myst:project#index)",
        "<src>/index.md:3: WARNING: Multiple matches found for target 'local:?:?:index' in 'local:std:label:index','local:std:doc:index' [myst.xref_duplicate]",  # noqa: E501
    ),
    (
        "myst_project_label",
        "(index)=\n# Title\n[](myst:project?o=label#index)",
        None,
    ),
    ("myst_project_regex", "(target)=\n# Title\n[](myst:project?regex#.*get)", None),
    ("myst_inv", "[](myst:inv#ref)", None),
    ("myst_inv_text", "[*text*](myst:inv#ref)", None),
    (
        "myst_inv_missing",
        "[*text*](myst:inv#xxx)",
        "<src>/index.md:1: WARNING: Unmatched target '?:?:?:xxx' [myst.iref_missing]",
    ),
    (
        "myst_inv_duplicate",
        "[*text*](myst:inv?regex#.*modindex)",
        "<src>/index.md:1: WARNING: Multiple matches found for target '?:?:?:.*modindex' in "
        "'project:std:label:modindex','project:std:label:py-modindex' [myst.iref_duplicate]",
    ),
]


@pytest.mark.parametrize(
    "test_name,text,warning",
    PARAMS,
    ids=[ps[0] for ps in PARAMS],
)
def test_parse(
    test_name: str,
    text: str,
    warning: bool,
    sphinx_doctree: CreateDoctree,
    file_regression,
    monkeypatch,
):
    monkeypatch.setattr(console, "codes", {})  # turn off coloring of warnings
    if "myst_inv" in test_name:
        sphinx_doctree.set_conf(
            {
                "extensions": ["myst_parser", "sphinx.ext.intersphinx"],
                "intersphinx_mapping": {
                    "project": ("https://project.com", str(STATIC / "objects_v2.inv"))
                },
            }
        )
    else:
        sphinx_doctree.set_conf({"extensions": ["myst_parser"]})
    sphinx_doctree.srcdir.joinpath("other.txt").write_text("hi", encoding="utf8")
    result = sphinx_doctree(text, "index.md")

    doctree = result.get_resolved_doctree("index")

    if warning is not None:
        assert result.warnings.strip() == warning
    else:
        assert not result.warnings

    doctree["source"] = "root/index.md"
    file_regression.check(doctree.pformat(), basename=test_name, extension=".xml")
