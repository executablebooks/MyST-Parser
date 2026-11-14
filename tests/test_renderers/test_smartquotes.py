"""Tests for localized quote rules with the MyST ``smartquotes`` extension (#806)."""

from __future__ import annotations

import pytest
from docutils import nodes
from docutils.utils.smartquotes import smartchars
from sphinx_pytest.plugin import CreateDoctree


@pytest.mark.parametrize(
    ("language", "sphinx_smartquotes", "expected"),
    [
        pytest.param(
            "fr",
            True,
            "Welcome to Test\u2019s documentation!\n\n\u00ab\u00a0Test\u00a0\u00bb and \u201csingle\u201d",
            id="fr-with-sphinx-smartquotes",
        ),
        pytest.param(
            "fr",
            False,
            "Welcome to Test\u2019s documentation!\n\n\u00ab\u00a0Test\u00a0\u00bb and \u201csingle\u201d",
            id="fr-myst-only",
        ),
        pytest.param(
            "de",
            False,
            "Welcome to Test\u2019s documentation!\n\n\u201eTest\u201c and \u201asingle\u2018",
            id="de-myst-only",
        ),
        pytest.param(
            "fr_CH",
            False,
            "Welcome to Test\u2019s documentation!\n\n\u00abTest\u00bb and \u2039single\u203a",
            id="fr-ch-subtag",
        ),
        pytest.param(
            "ja",
            False,
            "Welcome to Test\u2019s documentation!\n\n\u300cTest\u300d and \u300esingle\u300f",
            id="ja-myst-only",
        ),
        pytest.param(
            "ar",
            False,
            "Welcome to Test\u2019s documentation!\n\n\u201cTest\u201d and \u2018single\u2019",
            id="unsupported-smartquotes-language-fallback",
        ),
    ],
)
def test_sphinx_smartquotes_language(
    sphinx_doctree: CreateDoctree,
    language: str,
    sphinx_smartquotes: bool,
    expected: str,
) -> None:
    """Sphinx ``language`` localizes MyST's ``smartquotes`` extension (#806)."""
    sphinx_doctree.set_conf(
        {
            "extensions": ["myst_parser"],
            "myst_enable_extensions": ["smartquotes"],
            "language": language,
            "smartquotes": sphinx_smartquotes,
        }
    )
    result = sphinx_doctree(
        "# Welcome to Test's documentation!\n\n\"Test\" and 'single'\n",
        "index.md",
    )
    assert not result.warnings
    assert result.doctrees["index"].astext() == expected


def test_sphinx_smartquotes_topmatter_and_include(
    sphinx_doctree: CreateDoctree,
) -> None:
    """Per-file front matter and ``{include}`` directives honor Sphinx ``language`` (#806)."""
    sphinx_doctree.srcdir.joinpath("included.md").write_text(
        "\"Included\" and 'nested'\n",
        encoding="utf8",
    )
    sphinx_doctree.set_conf(
        {
            "extensions": ["myst_parser"],
            "language": "fr",
            "smartquotes": False,
            "exclude_patterns": ["included.md"],
        }
    )
    source = (
        "---\n"
        "myst:\n"
        "  enable_extensions:\n"
        "    - smartquotes\n"
        "---\n"
        "# Heading\n\n"
        '"Main"\n\n'
        "```{include} included.md\n"
        "```\n"
    )
    result = sphinx_doctree(source, "index.md")
    assert not result.warnings
    paragraphs = [p.astext() for p in result.doctrees["index"].findall(nodes.paragraph)]
    assert paragraphs == [
        "\u00ab\u00a0Main\u00a0\u00bb",
        "\u00ab\u00a0Included\u00a0\u00bb and \u201cnested\u201d",
    ]


def test_sphinx_smartquotes_env_locales_no_global_mutation(
    sphinx_doctree: CreateDoctree,
) -> None:
    """Custom ``env.settings['smartquotes_locales']`` works without mutating Docutils globals."""
    snapshot = dict(smartchars.quotes)
    (sphinx_doctree.srcdir / "ext_locales.py").write_text(
        "def setup(app):\n"
        "    app.connect(\n"
        "        'builder-inited',\n"
        "        lambda app: app.env.settings.update({\n"
        "            'smartquotes_locales': [('fr', ('[[', ']]', '{{', '}}'))],\n"
        "        }),\n"
        "    )\n",
        encoding="utf8",
    )
    import sys

    sys.path.insert(0, str(sphinx_doctree.srcdir))
    try:
        sphinx_doctree.set_conf(
            {
                "extensions": ["myst_parser", "ext_locales"],
                "myst_enable_extensions": ["smartquotes"],
                "language": "fr",
                "smartquotes": False,
            }
        )
        result = sphinx_doctree("# Title\n\n\"Double\" and 'single'\n", "index.md")
    finally:
        sys.path.remove(str(sphinx_doctree.srcdir))
        sys.modules.pop("ext_locales", None)

    assert not result.warnings
    assert result.doctrees["index"].astext() == "Title\n\n[[Double]] and {{single}}"
    assert smartchars.quotes == snapshot
