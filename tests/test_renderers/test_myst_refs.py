from pathlib import Path

import pytest
import yaml
from sphinx.util import console
from sphinx_pytest.plugin import CreateDoctree

STATIC = Path(__file__).parent.absolute() / ".." / "static"
FIXTURES = Path(__file__).parent.absolute() / "fixtures"


@pytest.mark.param_file(FIXTURES / "myst_references.md")
def test_parse(
    file_params,
    sphinx_doctree: CreateDoctree,
    monkeypatch,
):
    monkeypatch.setattr(console, "codes", {})  # turn off coloring of warnings
    sphinx_doctree.buildername = "html"
    conf = {"extensions": ["myst_parser"]}
    if "[ADD_ANCHORS]" in file_params.title:
        conf["myst_heading_anchors"] = 2
    if "[LOAD_INV]" in file_params.title:
        conf["extensions"].append("sphinx.ext.intersphinx")
        conf["intersphinx_mapping"] = {
            "project": ("https://project.com", str(STATIC / "objects_v2.inv"))
        }
    sphinx_doctree.set_conf(conf)
    sphinx_doctree.srcdir.joinpath("index.md").write_text(
        "# Main\n```{toctree}\ntest\nother\n```", encoding="utf8"
    )
    sphinx_doctree.srcdir.joinpath("other.md").write_text(
        "(ref2)=\n# Other", encoding="utf8"
    )
    sphinx_doctree.srcdir.joinpath("other.txt").write_text("hi", encoding="utf8")
    result = sphinx_doctree(file_params.content, "test.md")

    # get warnings before we run the doctree resolution (and thus post-transforms) again
    warnings = result.warnings.strip()

    doctree = result.get_resolved_doctree("test")
    doctree["source"] = "root/test.md"
    output = doctree.pformat()
    if warnings:
        output += "\n" + warnings
    file_params.assert_expected(output, rstrip_lines=True)


def test_suppress_warnings(sphinx_doctree: CreateDoctree):
    sphinx_doctree.set_conf(
        {
            "extensions": ["myst_parser"],
            "suppress_warnings": ["myst.invalid_uri"],
        }
    )
    result = sphinx_doctree("[](ref)", "index.md")

    assert not result.warnings


def test_objects_builder(sphinx_doctree: CreateDoctree, data_regression):
    sphinx_doctree.buildername = "myst_refs"
    sphinx_doctree.set_conf(
        {
            "extensions": ["myst_parser", "sphinx.ext.intersphinx"],
            "project": "test",
            "version": "0.0.1",
            "intersphinx_mapping": {
                "other": ("https://project.com", str(STATIC / "objects_v2.inv"))
            },
        }
    )
    result = sphinx_doctree("(target)=\n# Head\n", "index.md")
    assert {p.name for p in Path(result.app.outdir).iterdir()} == {
        "project.yaml",
        "local.yaml",
        "inv.other.yaml",
    }
    opath = Path(result.app.outdir).joinpath("project.yaml")
    assert opath.exists()
    data_regression.check(yaml.safe_load(opath.read_text()))
