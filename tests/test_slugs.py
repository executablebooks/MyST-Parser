"""Tests for :mod:`myst_parser.slugs`.

The cases are stored in a language-agnostic data corpus
(``tests/fixtures/slugs.json``), so that alternative MyST implementations
can reuse them; see the module docstring of ``myst_parser.slugs``.
"""

import json
from pathlib import Path

import pytest

from myst_parser.slugs import SLUG_PRESETS, unique_slug

CORPUS = json.loads(
    Path(__file__).parent.joinpath("fixtures", "slugs.json").read_text("utf8")
)


@pytest.mark.parametrize(
    "record",
    CORPUS["slugify"],
    ids=[f"{r['preset']}-{r['input']}" for r in CORPUS["slugify"]],
)
def test_slugify(record):
    """Each preset slugify function matches the corpus."""
    slug_func = SLUG_PRESETS[record["preset"]]
    assert slug_func(record["input"]) == record["expected"]


@pytest.mark.parametrize(
    "record",
    CORPUS["unique"],
    ids=[f"{r['slug']}-in-{r['existing']}" for r in CORPUS["unique"]],
)
def test_unique_slug(record):
    """``unique_slug`` suffixes against existing slugs (x, x-1, x-2, ...)."""
    assert unique_slug(record["slug"], record["existing"]) == record["expected"]


def test_slug_presets_keys():
    """The presets are exactly the documented ones."""
    assert set(SLUG_PRESETS) == {"docutils", "github", "gitlab"}


@pytest.mark.parametrize(
    "title",
    [record["input"] for record in CORPUS["slugify"]]
    + [
        # extra fidelity vectors, beyond the corpus
        "Ærøskøbing",  # digraph + stroked o
        "øđħıłŧ",  # the whole translate table: head ...
        "ƀƃƈƌƒƙƚƞƥƫƭƴƶ",  # ... middle ...
        "ǥȥȴȵȶȷȼȿɀɇɉɋɍɏ",  # ... and tail (6 + 13 + 14 = all 33 entries)
        "élégant",  # combining acute accents (NFKD)
        "① ² ⅓ Ⅳ",  # numeric compatibility forms
        "ﬁne ﬂow ǆungle",  # ligature compatibility forms
        "  tabs\tand\nnewlines  ",  # whitespace normalization
        "-- leading -- trailing --",
        "123",  # digits only -> empty
        "𝔘𝔫𝔦𝔠𝔬𝔡𝔢",  # noqa: RUF001  (mathematical alphanumerics, NFKD to ascii)
        "ıstanbul I",  # noqa: RUF001  (dotless i / turkish-locale hazard)
        "",  # empty input
    ],
    ids=repr,
)
def test_docutils_preset_fidelity(title):
    """The ``docutils`` preset is byte-identical to ``docutils.nodes.make_id``.

    This pins fidelity by CI: a future docutils change to ``make_id`` fails
    here, surfacing the drift instead of letting the two silently diverge
    (contract policy: the preset and corpus then stay byte-stable, and the
    divergence is documented).
    """
    from docutils.nodes import make_id

    assert SLUG_PRESETS["docutils"](title) == make_id(title)


def test_slugs_module_has_no_third_party_deps():
    """``myst_parser.slugs`` is pure standard library.

    This keeps it trivially portable for other MyST implementations.
    """
    import ast

    source = Path(SLUG_PRESETS["github"].__code__.co_filename).read_text("utf8")
    imported = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            imported.add(node.module.split(".")[0])
    assert imported <= {"__future__", "re", "collections", "typing", "unicodedata"}


def test_corpus_metadata():
    """The corpus carries its contract version and policy."""
    assert CORPUS["version"] == 1
    assert "append-only" in CORPUS["description"]
