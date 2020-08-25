MyST - Markedly Structured Text
===============================

[![PyPI][pypi-badge]][pypi-link]
[![Conda][conda-badge]][conda-link]

**A fully-functional markdown flavor and parser for Sphinx.**

MyST allows you to write Sphinx documentation entirely in markdown.
MyST markdown provides a markdown equivalent of the reStructuredText syntax,
meaning that you can do anything in MyST that you can do with reStructuredText.
It is an attempt to have the best of both worlds: the flexibility
and extensibility of Sphinx with the simplicity and readability of Markdown.

MyST has the following main features:

* **[A markdown parser for Sphinx](parse-with-sphinx)**. You can write your entire
  {doc}`Sphinx documentation <sphinx:usage/quickstart>` in Markdown.
* **[Call Sphinx directives and roles from within Markdown](syntax/directives)**,
  allowing you to extend your document via Sphinx extensions.
* **[Extended Markdown syntax for useful rST features](extended-block-tokens)**, such
  as line commenting and footnotes.
* **[A Sphinx-independent parser of MyST markdown](using/use_api)** that can be extended
  to add new functionality and outputs for MyST.
* **[A superset of CommonMark markdown][commonmark]**. Any CommonMark markdown
  (such as Jupyter Notebook markdown) is natively supported by the MyST parser.

You may use MyST markdown **in addition to** using reStructuredText in Sphinx.
See {doc}`using/intro` to get started.

## Site contents

```{toctree}
---
maxdepth: 2
caption: Using MyST Markdown
---
using/intro.md
using/syntax.md
using/howto.md
using/faq.md
using/use_api.md
```

```{toctree}
---
maxdepth: 2
caption: Reference and contributing
---
examples/index.md
develop/index.md
api/index.md
GitHub repo <https://github.com/executablebooks/myst-parser>
```

## Why MyST markdown?

While markdown is ubiquitous, it is not powerful enough for writing modern,
fully-featured documentation. Some flavors of markdown support features needed for this,
but there is no community standard around various syntactic choices for these features.

Sphinx is a documentation generation framework written in Python. It heavily-utilizes
reStructuredText syntax, which is another markup language for writing documents. In
particular, Sphinx defines two extension points that are extremely useful:
**{ref}`in-line roles<sphinx:rst-roles-alt>`** and **{ref}`block-level directives <sphinx:rst-directives>`**.

**This project is an attempt at combining the simplicity and readability of Markdown
with the power and flexibility of reStructuredText and the Sphinx platform.** It
starts with the [CommonMark markdown specification][commonmark], and selectively adds a few extra
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

## Acknowledgements

The MyST markdown language and MyST parser are both supported by the open community,
[The Executable Book Project](https://executablebooks.org).

[commonmark]: https://commonmark.org/
[github-ci]: https://github.com/executablebooks/MyST-Parser/workflows/continuous-integration/badge.svg?branch=master
[github-link]: https://github.com/executablebooks/MyST-Parser
[codecov-badge]: https://codecov.io/gh/executablebooks/MyST-Parser/branch/master/graph/badge.svg
[codecov-link]: https://codecov.io/gh/executablebooks/MyST-Parser
[rtd-badge]: https://readthedocs.org/projects/myst-parser/badge/?version=latest
[rtd-link]: https://myst-parser.readthedocs.io/en/latest/?badge=latest
[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[pypi-badge]: https://img.shields.io/pypi/v/myst-parser.svg
[pypi-link]: https://pypi.org/project/myst-parser
[conda-badge]: https://anaconda.org/conda-forge/myst-parser/badges/version.svg
[conda-link]: https://anaconda.org/conda-forge/myst-parser
[black-link]: https://github.com/ambv/black
[github-badge]: https://img.shields.io/github/stars/executablebooks/myst-parser?label=github
