import pytest
from sphinx_pytest.plugin import CreateDoctree


@pytest.mark.parametrize(
    "test_name,text,should_warn",
    [
        ("null", "", False),
        ("missing", "[](ref)", True),
        ("doc_with_extension", "[](index.md)", False),
        ("doc_nested", "[*text*](index.md)", False),
        ("ref", "(ref)=\n# Title\n[](#ref)", False),
        ("ref_nested", "(ref)=\n# Title\n[*text*](#ref)", False),
        ("ref_colon", "(ref:colon)=\n# Title\n[](#ref:colon)", False),
        # myst scheme
        ("myst-doc", "[](myst:any#index)", False),
        ("myst-duplicate", "(index)=\n# Title\n[](myst:any#index)", True),
    ],
)
def test_parse(
    test_name: str,
    text: str,
    should_warn: bool,
    sphinx_doctree: CreateDoctree,
    file_regression,
):
    sphinx_doctree.set_conf({"extensions": ["myst_parser"]})
    result = sphinx_doctree(text, "index.md")

    doctree = result.get_resolved_doctree("index")

    if should_warn:
        assert result.warnings
    else:
        assert not result.warnings

    doctree["source"] = "root/index.md"
    file_regression.check(doctree.pformat(), basename=test_name, extension=".xml")
