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
    """The presets are exactly the two documented ones."""
    assert set(SLUG_PRESETS) == {"github", "gitlab"}


def test_slugs_module_has_no_third_party_deps():
    """``myst_parser.slugs`` is pure standard library (only ``re``, ``typing``).

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
    assert imported <= {"__future__", "re", "collections", "typing"}
