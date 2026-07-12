"""Slug generation for heading anchors.

This is the single source of truth for heading slugs,
shared by the renderer (``myst_heading_anchors``) and the ``myst-anchors`` CLI.

The functions here are pure and dependency-free (standard library ``re`` only),
so that alternative implementations of MyST can replicate them from this file;
for the same reason, the unit-test corpus is kept as a language-agnostic
data file (``tests/fixtures/slugs.json``).
"""

from __future__ import annotations

import re
from collections.abc import Callable, Container

_GITHUB_CLEAN = re.compile(r"[^\w\u4e00-\u9fff\- ]")


def github_slugify(title: str) -> str:
    """Convert a heading title to a GitHub-style slug.

    Algorithm: lowercase the title; replace spaces with hyphens ``-``;
    remove every character that is not a word character (``\\w``),
    a CJK ideograph (U+4E00-U+9FFF), a hyphen or a space.

    Leading/trailing whitespace is deliberately *not* stripped first,
    so it survives as leading/trailing hyphens
    (e.g. ``" a b "`` -> ``"-a-b-"``); see the v0.18.1 changelog.

    See https://github.com/jch/html-pipeline/blob/master/lib/html/pipeline/toc_filter.rb
    and https://gist.github.com/asabaylus/3071099
    """
    return _GITHUB_CLEAN.sub("", title.lower().replace(" ", "-"))


_GITLAB_CLEAN = re.compile(r"[^\w\- ]")
_GITLAB_DIGITS = re.compile(r"\d+")
_GITLAB_SQUEEZE = re.compile(r"-{2,}")


def gitlab_slugify(title: str) -> str:
    """Convert a heading title to a GitLab-style slug.

    Algorithm: strip and lowercase the title; remove every character that is
    not a word character (``\\w``), a hyphen or a space; replace spaces with
    hyphens; squeeze consecutive hyphens; prefix ``anchor-`` if the result
    consists only of digits.

    See https://docs.gitlab.com/ee/user/markdown.html#heading-ids-and-links
    and ``Gitlab::Utils::Markdown#string_to_anchor``.
    """
    slug = _GITLAB_CLEAN.sub("", title.strip().lower()).replace(" ", "-")
    slug = _GITLAB_SQUEEZE.sub("-", slug)
    if _GITLAB_DIGITS.fullmatch(slug):
        slug = f"anchor-{slug}"
    return slug


SLUG_PRESETS: dict[str, Callable[[str], str]] = {
    "github": github_slugify,
    "gitlab": gitlab_slugify,
}
"""Named slugify functions, usable as ``myst_heading_slug_func`` values."""


def unique_slug(slug: str, existing: Container[str]) -> str:
    """Suffix ``slug`` with ``-1``, ``-2``, ... until it is not in ``existing``.

    The base never changes, so duplicates of ``x`` become
    ``x, x-1, x-2, ...`` (GitHub behaviour), not ``x, x-1, x-1-2, ...``.
    """
    uniq, i = slug, 1
    while uniq in existing:
        uniq = f"{slug}-{i}"
        i += 1
    return uniq
