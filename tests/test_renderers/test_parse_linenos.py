"""Test ``DocutilsRenderer._parse_linenos``.

This is the helper behind the ``emphasize-lines`` attribute,
and is only reached on the sphinx code path.
"""

import re

import pytest

from myst_parser.mdit_to_docutils.base import DocutilsRenderer


def test_parse_linenos():
    """A line within the block is returned, 1-based."""
    assert DocutilsRenderer._parse_linenos("2", 3) == [2]


def test_parse_linenos_out_of_range():
    """A line past the end of the block reports the allowed range."""
    with pytest.raises(ValueError, match=re.escape("out of range(1-3)")):
        DocutilsRenderer._parse_linenos("5", 3)
