# MyST - Markedly Structured Text <img src="_static/logo-square.svg" width=40 />

[![PyPI][pypi-badge]][pypi-link]
[![Conda][conda-badge]][conda-link]

**MyST is a rich and extensible flavor of Markdown meant for technical documentation and publishing**.

MyST is a flavor of markdown that is designed for simplicity, flexibility, and extensibility. Here are a few major features

:::{panels}
:container: +full-width text-center
:column: col-4 px-2 py-2
:card:

**[CommonMark compliant](commonmark-block-tokens)** ✔
^^^
MyST is a superset of [CommonMark markdown][commonmark]. Any CommonMark document is also MyST-compliant.
---

**[Extra syntax for authoring](extended-block-tokens)** ✍
^^^
MyST extends CommonMark with [syntax meant for scholarly writing and technical documentation](extended-block-tokens).

---
**[Extendable syntax](syntax/directives)** 🚀
^^^
MyST provides [roles](syntax/roles) and [directives](syntax/directives), allowing you to extend MyST's functionality.

---
**[Compatible with Sphinx](sphinx/index.md)** 📄
^^^
MyST is inspired by Sphinx, and comes with [its own Sphinx parser](sphinx/index.md). [Write your Sphinx docs in markdown](sphinx:usage/quickstart)!

---
**[Hackable with Python](api/index.md)** 🐍
^^^
This MyST parser is built on top of the [`markdown-it-py` package][markdown-it-py], an pluggable Python parser for Markdown.

---
**[Hackable with Javascript][markdown-it-myst]** 🌍
^^^
The [Javascript parser][markdown-it-myst] builds on [markdown-it][markdown-it], and allows you to parse MyST in websites.
:::

:::{seealso}
For some examples of how MyST can be used, check out the [Jupyter Book project](https://jupyterbook.org), which uses MyST Markdown heavily, as well as [the Jupyter Book gallery](https://gallery.jupyterbook.org) which contains a list of books built by others, all using MyST.
:::

## Get started

These pages cover step-by-step instructions to get started with MyST Markdown.

```{toctree}
:maxdepth: 2
sphinx/intro.md
```

## MyST Syntax

These sections cover the syntax that makes up MyST Markdown, some common use-cases that it supports, as well as a few extensions that allow you to enable new features with MyST.

```{toctree}
:caption: MyST Syntax
:maxdepth: 2
syntax/syntax
syntax/syntax-optional
syntax/reference
```

## Topic Guides

Topic guides cover particular tools, use-cases, and functionality in the MyST ecosystem.

```{toctree}
:maxdepth: 2
:caption: Topic Guides
explain/index.md
sphinx/index.md
api/index.md
develop/index.md
```

## About the project

These sections cover "meta" information about the MyST Markdown project.

```{toctree}
:maxdepth: 2
:caption: About the project
examples/index.md
develop/_changelog.md
GitHub repo <https://github.com/executablebooks/myst-parser>
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
[markdown-it-py]: https://markdown-it-py.readthedocs.io/
[markdown-it-myst]: https://github.com/executablebooks/markdown-it-myst
[markdown-it]: https://markdown-it.github.io/
