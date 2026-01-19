"""Shared pytest configuration for all tests."""

import re

import pytest
from docutils import __version_info__ as docutils_version_info

DOCUTILS_0_22_PLUS = docutils_version_info >= (0, 22)


@pytest.fixture
def normalize_doctree_xml():
    """Normalize docutils XML output for cross-version compatibility.

    In docutils 0.22+, boolean attributes are serialized as "1"/"0"
    instead of "True"/"False". This function normalizes to the old format
    for consistent test fixtures.
    """

    def _normalize(text: str) -> str:
        if DOCUTILS_0_22_PLUS:
            # Normalize new format (1/0) to old format (1/0)
            # Only replace when it's clearly a boolean attribute value
            # Pattern: attribute="1" or attribute="0"
            attrs = [
                "force",
                "glob",
                "hidden",
                "id_link",
                "includehidden",
                "inline",
                "internal",
                "is_div",
                "linenos",
                "multi_line_parameter_list",
                "multi_line_trailing_comma",
                "no-contents-entry",
                "no-index",
                "no-index-entry",
                "no-typesetting",
                "no-wrap",
                "nocontentsentry",
                "noindex",
                "noindexentry",
                "nowrap",
                "refexplicit",
                "refspecific",
                "refwarn",
                "sorted",
                "titlesonly",
                "toctree",
                "translatable",
            ]
            text = re.sub(rf' ({"|".join(attrs)})="1"', r' \1="True"', text)
            text = re.sub(rf' ({"|".join(attrs)})="0"', r' \1="False"', text)
            # numbered is changed in math_block, but not in toctree, so we have to be more precise
            text = re.sub(r' numbered="1" xml:space', r' numbered="True" xml:space', text)
        return text

    return _normalize
