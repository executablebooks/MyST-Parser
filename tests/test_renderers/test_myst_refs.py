from pathlib import Path

import pytest
import yaml
from sphinx import version_info
from sphinx.util import console
from sphinx_pytest.plugin import CreateDoctree

from myst_parser.sphinx_ext.references import project_inventory

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
    if "[NUMBERED]" in file_params.title:
        conf["numfig"] = True
        conf["numfig_secnum_depth"] = 2
        conf["myst_link_placeholders"] = True
    if "[ADD_ANCHORS]" in file_params.title:
        conf["myst_heading_anchors"] = 2
    if "[LOAD_INV]" in file_params.title:
        conf["extensions"].append("sphinx.ext.intersphinx")
        conf["intersphinx_mapping"] = {
            "project": ("https://project.com", str(STATIC / "objects_v2.inv"))
        }
    sphinx_doctree.set_conf(conf)
    sphinx_doctree.srcdir.joinpath("index.md").write_text(
        f"""\
# Main
```{{toctree}}
{':numbered:' if '[NUMBERED]' in file_params.title else ''}
test
other
```
""",
        encoding="utf8",
    )
    sphinx_doctree.srcdir.joinpath("other.md").write_text(
        """\
(ref2)=
(duplicate)=
# Other

```{glossary}
term1
  description ...

duplicate
  description ...
```
""",
        encoding="utf8",
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


@pytest.mark.skipif(
    version_info[0] < 5,
    reason="latex output changed in sphinx 5",
)
@pytest.mark.param_file(FIXTURES / "myst_references_latex.md")
def test_latex_builds(
    file_params,
    sphinx_doctree: CreateDoctree,
    monkeypatch,
):
    monkeypatch.setattr(console, "codes", {})  # turn off coloring of warnings
    sphinx_doctree.buildername = "latex"
    conf = {
        "extensions": ["myst_parser"],
        "project": "test",
        "templates_path": ["_templates"],
        "myst_link_placeholders": True,
    }
    if "[NUMBERED]" in file_params.title:
        conf["numfig"] = True
        conf["numfig_secnum_depth"] = 2
        conf["myst_link_placeholders"] = True
    sphinx_doctree.set_conf(conf)
    sphinx_doctree.srcdir.joinpath("_templates").mkdir()
    sphinx_doctree.srcdir.joinpath("_templates", "latex.tex_t").write_text(
        "<%= body %>\n", encoding="utf8"
    )
    sphinx_doctree.srcdir.joinpath("index.md").write_text(
        f"""\
# Main
```{{toctree}}
{':numbered:' if '[NUMBERED]' in file_params.title else ''}
test
```
""",
        encoding="utf8",
    )
    result = sphinx_doctree(file_params.content, "test.md")
    warnings = result.warnings.strip()
    output = Path(result.app.outdir).joinpath("test.tex").read_text(encoding="utf8")
    output = "\n".join([line for line in output.splitlines() if line])
    if warnings:
        output += "\n" + warnings
    file_params.assert_expected(output, rstrip_lines=True)


def test_build_numbered_singlehtml(sphinx_doctree: CreateDoctree, data_regression):
    sphinx_doctree.buildername = "singlehtml"
    sphinx_doctree.set_conf(
        {
            "project": "test",
            "extensions": ["myst_parser"],
            "numfig": True,
            "numfig_secnum_depth": 2,
            "myst_link_placeholders": True,
        }
    )
    sphinx_doctree.srcdir.joinpath("index.md").write_text(
        """
# Head

```{toctree}
:numbered:
page
```

START
[{number} {name}](#section1)
[{number} {name}](#figure1)
[{number} {name}](#code1)
[{number} {name}](#table1)
[{number}](#eq1)
END
"""
    )
    result = sphinx_doctree(
        """
# Section
## Sub-section 1
(section1)=
## Sub-section 2

```{figure} https://example.com
:name: figure1
Caption figure
```

```{code-block} python
:caption: Caption code
:name: code1
a = 1
```

```{table} Caption table
:name: table1
a  | b
-- | --
```

```{math}
:label: eq1
a = 1
```
""",
        "page.md",
    )
    assert not result.warnings
    output = Path(result.app.outdir).joinpath("index.html").read_text(encoding="utf8")
    output = output.split("START")[1].split("END")[0].strip()
    print(output)
    data_regression.check(output)


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
            "myst_heading_anchors": 1,
            "project": "test",
            "version": "0.0.1",
            "intersphinx_mapping": {
                "other": ("https://project.com", str(STATIC / "objects_v2.inv"))
            },
        }
    )
    sphinx_doctree.srcdir.joinpath("index.md").write_text(
        """
# Head

```{toctree}
:numbered:
page
```
"""
    )
    result = sphinx_doctree("(target)=\n# Head\n", "page.md")
    file_names = {
        "project.yaml",
        "anchors.yaml",
        "inv.other.yaml",
    }
    assert {p.name for p in Path(result.app.outdir).iterdir()} == file_names
    data = {}
    for file_name in file_names:
        opath = Path(result.app.outdir).joinpath(file_name)
        data[file_name] = yaml.safe_load(opath.read_text())
    data_regression.check(data)


def test_project_inventory_numbering(sphinx_doctree: CreateDoctree, data_regression):
    sphinx_doctree.buildername = "myst_refs"
    sphinx_doctree.set_conf(
        {
            "extensions": ["myst_parser"],
            "numfig": True,
            "numfig_secnum_depth": 2,
        }
    )
    sphinx_doctree.srcdir.joinpath("index.md").write_text(
        """
# Head

```{toctree}
:numbered:
page
```
"""
    )
    result = sphinx_doctree(
        """
# Section

## Sub-section 1

## Sub-section 2

```{figure} https://example.com
:name: figure1
Caption
```

```{code-block} python
:caption: Caption
:name: code1
a = 1
```

```{table} Caption
:name: table1
a  | b
-- | --
```

```{math}
:label: eq1
a = 1
```
""",
        "page.md",
    )
    assert not result.warnings
    data = project_inventory(result.env, with_numbers=True)
    data_regression.check(data)
