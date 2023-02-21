import pytest
from sphinx_pytest.plugin import CreateDoctree


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
def test_parse(
    test_name: str,
    text: str,
    should_warn: bool,
    sphinx_doctree: CreateDoctree,
    file_regression,
):
    sphinx_doctree.set_conf({"extensions": ["myst_parser"]})
    result = sphinx_doctree(text, "index.md")
    assert not result.warnings

    doctree = result.get_resolved_doctree("index")

    if should_warn:
        assert result.warnings
    else:
        assert not result.warnings

    doctree["source"] = "root/index.md"
    outcome = doctree.pformat()
    if result.warnings.strip():
        outcome += "\n\n" + result.warnings.strip().replace("[91m", "").replace(
            "[39;49;00m", ""
        )
    file_regression.check(outcome, basename=test_name, extension=".xml")
