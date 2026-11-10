"""``§1.1`` section references resolve to the same heading in docutils and sphinx.

docutils promotes a lone top-level heading to the document title
(and a lone child heading of that to the subtitle), but sphinx never does,
so the two doctrees differ in shape.
The references are resolved before that promotion, against the headings as written,
so each case of ``fixtures/section_ref_resolution.md`` (the conformance contract)
is checked against both parsers, with the same expected result;
a resolution that ran after the promotion would fail the docutils side.
"""

from __future__ import annotations

import io
import re
from pathlib import Path

import pytest
from docutils import nodes
from docutils.core import publish_doctree
from pytest_param_files import ParamTestData
from sphinx.util.console import strip_colors
from sphinx_pytest.plugin import CreateDoctree

from myst_parser.parsers.docutils_ import Parser

FIXTURE_PATH = Path(__file__).parent.joinpath("fixtures")

_FILE_RE = re.compile(r"^-- file: (\S+)\n", re.MULTILINE)
_WARNING_RE = re.compile(
    r"Section reference target not found in this document: '([^']+)'"
)


def _split_files(content: str) -> tuple[str, dict[str, str]]:
    """Split a case into its document and its extra files (``-- file: <name>`` lines)."""
    parts = _FILE_RE.split(content)
    return parts[0], dict(zip(parts[1::2], parts[2::2], strict=True))


def _parse_options(description: str | None) -> tuple[bool, dict, dict, dict]:
    """Parse the case options into ``(sphinx_only, shared, docutils, sphinx)`` settings."""
    sphinx_only = False
    shared: dict = {}
    docutils_only: dict = {}
    sphinx_conf: dict = {"extensions": ["myst_parser"]}
    for option in (description or "").split():
        if option == "sphinx-only":
            sphinx_only = True
            continue
        key, value = option.split("=", 1)
        parsed = {"true": True, "false": False}.get(value, value)
        if key == "sphinx:extensions":
            sphinx_conf["extensions"] += value.split(",")
        elif key.startswith("sphinx:"):
            sphinx_conf[key.removeprefix("sphinx:")] = parsed
        elif key.startswith("docutils:"):
            docutils_only[key.removeprefix("docutils:")] = parsed
        else:
            shared[key] = parsed
    return sphinx_only, shared, docutils_only, sphinx_conf


def _is_inert(node: nodes.Element) -> bool:
    """Whether a marker sits in a context where references are never linked (R3).

    In docutils, a section title may have been promoted to the document title or subtitle.
    """
    parent = node.parent
    while parent is not None:
        if (
            isinstance(parent, nodes.reference)
            or parent.tagname == "pending_xref"
            or _is_section_title(parent)
        ):
            return True
        parent = parent.parent
    return False


def _is_section_title(node: nodes.Node) -> bool:
    """Whether a node is a section title (in docutils, maybe promoted to the document).

    A sidebar's subtitle is not one.
    """
    return isinstance(node, (nodes.title, nodes.subtitle)) and isinstance(
        node.parent, (nodes.section, nodes.document)
    )


def _target_title(doctree: nodes.document, refid: str) -> str:
    """Return the title of the section that holds ``refid``.

    ``[k]`` is added if it is the k-th of several sections with that title,
    and ``@refid`` if the id comes from an explicit target.
    """
    target = next(
        node for node in doctree.findall(nodes.Element) if refid in node["ids"]
    )
    if isinstance(target, (nodes.section, nodes.document)):
        target = next(
            child for child in target.children if isinstance(child, nodes.title)
        )
    text = target.astext()
    same = [
        node for node in doctree.findall(_is_section_title) if node.astext() == text
    ]
    if len(same) > 1:
        text += f" [{next(i for i, node in enumerate(same, 1) if node is target)}]"
    # an explicit target, such as ``(label)=``, leaves a ``target`` that points to it
    if any(node.get("refid") == refid for node in doctree.findall(nodes.target)):
        text += f" @{refid}"
    return text


def _outcome(doctree: nodes.document, warnings: str) -> str:
    """Summarise every reference, in document order, as in the fixture file.

    Each marker left unlinked is classed by its context, ``inert`` or ``unresolved``,
    and the ``unresolved`` ones must be exactly the ones that warned.
    """
    lines = []
    unresolved = []
    for node in doctree.findall(nodes.Element):
        if isinstance(node, nodes.reference) and "section-ref" in node["classes"]:
            lines.append(f"{node.astext()} -> {_target_title(doctree, node['refid'])}")
        elif isinstance(node, nodes.inline) and "section_numbers" in node:
            if _is_inert(node):
                lines.append(f"{node.astext()} inert")
            else:
                lines.append(f"{node.astext()} unresolved")
                unresolved.append(node.astext())
    assert sorted(_WARNING_RE.findall(warnings)) == sorted(unresolved)
    return "\n".join(lines)


def _summarise(doctree: nodes.document) -> tuple[list, list]:
    """Return the resolved ``(text, refid)`` pairs and the texts left unresolved."""
    resolved = [
        (ref.astext(), ref["refid"])
        for ref in doctree.findall(nodes.reference)
        if "section-ref" in ref["classes"]
    ]
    unresolved = [
        node.astext()
        for node in doctree.findall(nodes.inline)
        if "section_numbers" in node
    ]
    return resolved, unresolved


@pytest.mark.param_file(FIXTURE_PATH / "section_ref_resolution.md")
def test_resolution(
    file_params: ParamTestData, sphinx_doctree: CreateDoctree, tmp_path: Path
):
    """Each conformance case gives the expected outcome in both docutils and sphinx."""
    source, files = _split_files(file_params.content)
    sphinx_only, shared, docutils_only, sphinx_conf = _parse_options(
        file_params.description
    )

    if not sphinx_only:
        (tmp_path / "docutils").mkdir()
        for name, text in files.items():
            (tmp_path / "docutils" / name).write_text(text, encoding="utf8")
        warnings = io.StringIO()
        doctree = publish_doctree(
            source,
            source_path=str(tmp_path / "docutils" / "index.md"),
            parser=Parser(),
            settings_overrides={
                "myst_enable_extensions": ["section_ref"],
                "warning_stream": warnings,
                **shared,
                **docutils_only,
            },
        )
        file_params.assert_expected(
            _outcome(doctree, warnings.getvalue()), rstrip_lines=True
        )

    for name, text in files.items():
        sphinx_doctree.srcdir.joinpath(name).write_text(text, encoding="utf8")
    sphinx_doctree.set_conf(
        {
            "myst_enable_extensions": ["section_ref"],
            # extra files are only included, not documents of their own
            "exclude_patterns": list(files),
            **shared,
            **sphinx_conf,
        }
    )
    result = sphinx_doctree(source, "index.md")
    file_params.assert_expected(
        _outcome(result.doctrees["index"], result.warnings), rstrip_lines=True
    )


def test_docutils_without_doctitle_promotion():
    """With ``doctitle_xform`` off, docutils keeps the headings as sphinx does."""
    doctree = publish_doctree(
        "# T\n\nSee §1 and §1.1.\n\n## A\n\n### A1\n",
        parser=Parser(),
        settings_overrides={
            "myst_enable_extensions": ["section_ref"],
            "doctitle_xform": False,
        },
    )
    assert _summarise(doctree) == ([("§1", "a"), ("§1.1", "a1")], [])


def test_docutils_section_subtitles():
    """With ``sectsubtitle_xform`` on, references still follow the headings as written.

    docutils' ``SectSubTitle`` transform promotes C, the lone subsection of B,
    to B's subtitle, but C is still ``§1.1.1``, as it is in sphinx.
    """
    doctree = publish_doctree(
        "# T\n\n## A\n\nSee §1.1 and §1.1.1.\n\n### B\n\n#### C\n\nx\n",
        parser=Parser(),
        settings_overrides={
            "myst_enable_extensions": ["section_ref"],
            "sectsubtitle_xform": True,
        },
    )
    assert any(
        isinstance(node.parent, nodes.section)
        for node in doctree.findall(nodes.subtitle)
    ), "the section subtitle promotion did not happen"
    assert _summarise(doctree) == ([("§1.1", "b"), ("§1.1.1", "c")], [])


def test_docutils_warning_location_in_include(tmp_path):
    """An unresolved reference in an included file is reported at that file."""
    (tmp_path / "index.md").write_text(
        "# T\n\n## A\n\n```{include} sub.md\n```\n", encoding="utf8"
    )
    (tmp_path / "sub.md").write_text("Para\n\nSee §7.\n", encoding="utf8")
    warnings = io.StringIO()
    publish_doctree(
        (tmp_path / "index.md").read_text(encoding="utf8"),
        source_path=str(tmp_path / "index.md"),
        parser=Parser(),
        settings_overrides={
            "myst_enable_extensions": ["section_ref"],
            "warning_stream": warnings,
        },
    )
    location = f"{tmp_path / 'sub.md'}:3: (WARNING/2)"
    assert f"{location} Section reference target not found" in warnings.getvalue()


def test_subtitle_tooltip():
    """A reference to the promoted subtitle carries its text as the tooltip."""
    doctree = publish_doctree(
        "# T\n\n## The *A*\n\nSee §1.\n",
        parser=Parser(),
        settings_overrides={"myst_enable_extensions": ["section_ref"]},
    )
    (ref,) = (
        ref
        for ref in doctree.findall(nodes.reference)
        if "section-ref" in ref["classes"]
    )
    assert ref["reftitle"] == "The A"


# an unresolvable number in a section heading and in link text, which stay inert,
# then one in the body, written with a leading zero
WARNING_SOURCE = "# T §9\n\n## A §9\n\n[see §9](#a-9) and §09.9.\n"
WARNING_MESSAGE = "Section reference target not found in this document: '§09.9'"


def test_docutils_warning_only_for_unresolved():
    """Only the unresolved body reference warns, with its number as written."""
    warnings = io.StringIO()
    publish_doctree(
        WARNING_SOURCE,
        source_path="index.md",
        parser=Parser(),
        settings_overrides={
            "myst_enable_extensions": ["section_ref"],
            "warning_stream": warnings,
        },
    )
    assert warnings.getvalue().splitlines() == [
        f"index.md:5: (WARNING/2) {WARNING_MESSAGE} [myst.section_ref]"
    ]


def test_sphinx_warning_only_for_unresolved(sphinx_doctree: CreateDoctree):
    """Only the unresolved body reference warns, with its number as written."""
    sphinx_doctree.set_conf(
        {"extensions": ["myst_parser"], "myst_enable_extensions": ["section_ref"]}
    )
    result = sphinx_doctree(WARNING_SOURCE, "index.md")
    # the source path uses the OS separator (``<src>\\index.md`` on Windows)
    assert strip_colors(result.warnings).replace("\\", "/").strip().splitlines() == [
        f"<src>/index.md:5: WARNING: {WARNING_MESSAGE} [myst.section_ref]"
    ]


def test_sphinx_warning_suppressed(sphinx_doctree: CreateDoctree):
    """``suppress_warnings = ["myst.section_ref"]`` silences the warning."""
    sphinx_doctree.set_conf(
        {
            "extensions": ["myst_parser"],
            "myst_enable_extensions": ["section_ref"],
            "suppress_warnings": ["myst.section_ref"],
        }
    )
    result = sphinx_doctree(WARNING_SOURCE, "index.md")
    assert strip_colors(result.warnings).strip() == ""
    assert _summarise(result.doctrees["index"])[1] == ["§9", "§9", "§9", "§09.9"]


def test_section_numbers_on_resolved_reference():
    """A resolved reference keeps the parsed number, as the unresolved marker does."""
    doctree = publish_doctree(
        "# T\n\n## A\n\n### A1\n\nSee §01.1 and §7.\n",
        parser=Parser(),
        settings_overrides={
            "myst_enable_extensions": ["section_ref"],
            "warning_stream": io.StringIO(),
        },
    )
    numbers = [
        (node.tagname, node.astext(), node["section_numbers"])
        for node in doctree.findall(nodes.Element)
        if "section_numbers" in node
    ]
    assert numbers == [("reference", "§01.1", [1, 1]), ("inline", "§7", [7])]
