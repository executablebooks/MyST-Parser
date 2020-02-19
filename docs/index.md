MyST - Markedly Structured Text
===============================

MyST is a markdown flavor that implements the best parts of reStructuredText.
It is a *slight* extension of CommonMark markdown.

This project provides a parser for this flavor of markdown, as well as a bridge between
MyST syntax and Sphinx. This allows for native markdown support for roles and
directives.

```{warn}
The MyST parser is in an alpha stage, and may have breaking syntax to its implementation
and to the syntax that it supports. Use at your own risk. If you find any issues,
please report them
[in the MyST issues](https://github.com/ExecutableBookProject/meta/issues/24)
```

## Why a new flavor of markdown?

While markdown is ubiquitous, it is not powerful enough for writing modern,
fully-featured documentation. Some flavors of markdown support features needed for this,
but there is no community standard around various syntactic choices for these features.

Sphinx is a documentation generation framework written in Python. It heavily-utilizes
reStructuredText syntax, which is another markup language for writing documents. In
particular, Sphinx defines two extension points that are extremely useful:
in-line **roles** and block-level **directives**.

**This project is an attempt at combining the simplicity and readability of Markdown
with the power and flexibility of reStructuredText and the Sphinx platform.** It
starts with the CommonMark markdown specification, and selectively adds a few extra
syntax pieces to utilize the most powerful parts of reStructuredText.

```{note}
The CommonMark community has been discussing an "official" extension syntax for many
years now (for example, see
[this seven-year-old thread about directives](https://talk.commonmark.org/t/generic-directives-plugins-syntax/444) as well as
[this more recent converstaion](https://talk.commonmark.org/t/support-for-extension-token/2771),
and [this comment listing several more threads on this topic](https://talk.commonmark.org/t/extension-terminology-and-rules/1233)).

We have chosen a "roles and directives" syntax that seems reasonable and follows other
common conventions in Markdown flavors. However, if the CommonMark community ever
decides on an "official" extension syntax, we will likely utilize this syntax for
MyST.
```

Here are the site contents:

```{toctree}
---
maxdepth: 2
caption: Contents
---
using/index.md
examples/index.md
develop/index.md
```
