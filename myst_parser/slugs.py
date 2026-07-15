"""Slug generation for heading anchors.

This is the single source of truth for heading slugs,
shared by the renderer (``myst_heading_anchors``) and the ``myst-anchors`` CLI.

The functions here are pure and dependency-free (standard library only),
so that alternative implementations of MyST can replicate them from this file;
for the same reason, the unit-test corpus is kept as a language-agnostic
data file (``tests/fixtures/slugs.json``).

A slug function may return an empty string (e.g. for a punctuation-only
title, or a non-Latin title under the ``docutils`` preset); an empty slug
means the heading gets *no* anchor.
"""

from __future__ import annotations

import re
import unicodedata
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


# ported verbatim from ``docutils.nodes`` (public domain), so that this
# module stays free of third-party imports; byte-fidelity to
# ``docutils.nodes.make_id`` is pinned by tests/test_slugs.py
_DOCUTILS_DIGRAPHS = {
    0x00DF: "sz",  # ß
    0x00E6: "ae",  # æ
    0x0153: "oe",  # œ
    0x0238: "db",  # ȸ
    0x0239: "qp",  # ȹ
}
_DOCUTILS_TRANSLATE = {
    0x00F8: "o",  # ø
    0x0111: "d",  # đ
    0x0127: "h",  # ħ
    0x0131: "i",  # dotless i
    0x0142: "l",  # ł
    0x0167: "t",  # ŧ
    0x0180: "b",  # ƀ
    0x0183: "b",  # ƃ
    0x0188: "c",  # ƈ
    0x018C: "d",  # ƌ
    0x0192: "f",  # ƒ
    0x0199: "k",  # ƙ
    0x019A: "l",  # ƚ
    0x019E: "n",  # ƞ
    0x01A5: "p",  # ƥ
    0x01AB: "t",  # ƫ
    0x01AD: "t",  # ƭ
    0x01B4: "y",  # ƴ
    0x01B6: "z",  # ƶ
    0x01E5: "g",  # ǥ
    0x0225: "z",  # ȥ
    0x0234: "l",  # ȴ
    0x0235: "n",  # ȵ
    0x0236: "t",  # ȶ
    0x0237: "j",  # ȷ
    0x023C: "c",  # ȼ
    0x023F: "s",  # ȿ
    0x0240: "z",  # ɀ
    0x0247: "e",  # ɇ
    0x0249: "j",  # ɉ
    0x024B: "q",  # ɋ
    0x024D: "r",  # ɍ
    0x024F: "y",  # ɏ
}
_DOCUTILS_NON_ID = re.compile(r"[^a-z0-9]+")
_DOCUTILS_AT_ENDS = re.compile(r"^[-0-9]+|-+$")


def docutils_slugify(title: str) -> str:
    """Convert a heading title to a docutils/reStructuredText-style id.

    Byte-identical to ``docutils.nodes.make_id``, for uniform anchors across
    mixed rST + Markdown projects.  Algorithm: lowercase the title; map the
    digraph letters ß æ œ ȸ ȹ and 33 further stroked/hooked Latin letters to
    ASCII equivalents; NFKD-normalize and drop every remaining non-ASCII
    character; collapse each run of characters outside ``[a-z0-9]`` to a
    single hyphen; strip leading digits/hyphens and trailing hyphens.

    The result matches ``[a-z](-?[a-z0-9]+)*`` — in particular it is *empty*
    for titles with no Latin letters (so such headings get no anchor), and
    docutils' own duplicate-id handling (``idN``) is not emulated:
    deduplication is governed by :func:`unique_slug`, whatever the preset.
    """
    slug = title.lower()
    slug = slug.translate(_DOCUTILS_DIGRAPHS)
    slug = slug.translate(_DOCUTILS_TRANSLATE)
    slug = unicodedata.normalize("NFKD", slug).encode("ascii", "ignore").decode()
    slug = _DOCUTILS_NON_ID.sub("-", " ".join(slug.split()))
    return _DOCUTILS_AT_ENDS.sub("", slug)


SLUG_PRESETS: dict[str, Callable[[str], str]] = {
    "docutils": docutils_slugify,
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
