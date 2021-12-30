# MyST - Markedly Structured Text <img src="_static/logo-square.svg" width=40 />

[](@x) [](@y) [](@y)

[![PyPI][pypi-badge]][pypi-link]
[![Conda][conda-badge]][conda-link]

**MyST is a rich and extensible flavor of Markdown meant for technical documentation and publishing**.

MyST is a flavor of markdown that is designed for simplicity, flexibility, and extensibility. Here are a few major features

:::{panels}
:container: +full-width text-center
:column: col-lg-4 px-2 py-2
:card:

**[CommonMark compliant](commonmark-block-tokens)** ✔
^^^
MyST is a superset of [CommonMark Markdown][commonmark]. Any CommonMark document is also MyST-compliant.
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
MyST is inspired by Sphinx, and comes with [its own Sphinx parser](sphinx/index.md).
[Write your Sphinx docs in Markdown](sphinx:usage/quickstart), or convert existing [RST to Markdown][rst-to-myst]
from the CLI or [using an interactive web interface][mystyc]!

---
**[Hackable with Python](api/index.md)** 🐍
^^^
This MyST parser is built on top of the [`markdown-it-py` package][markdown-it-py], an pluggable Python parser for Markdown.

---
**[Hackable with Javascript][markdown-it-myst]** 🌍
^^^
The [Javascript parser][markdown-it-myst] builds on [markdown-it][markdown-it], and allows you to parse MyST in websites.
:::

## Find the right documentation resources

This documentation is organized into a few major sections. **Tutorials** are step-by-step introductory guides to MyST Markdown. **Topic Guides** cover specific areas in more depth, and are organized as discrete "how-to" sections. **Reference** sections describe the API/syntax/etc of the MyST Parser in detail.

In addition, here are a few pointers to help you get started.

:::{panels}
:container: full-width
:column: col-lg-4 p-2
---
:header: bg-myst-one
**Get started with MyST**
^^^
**[](sphinx/intro.md)**: a step-by-step tutorial.

**[](syntax/syntax.md)**: discusses major MyST syntax components.

**[The Sphinx guide](sphinx/index.md)**: how to use MyST with your Sphinx documentation.
---
:header: bg-myst-two

**Learn more about MyST**
^^^
**[](syntax/optional.md)**: additional syntax you can enable for extra features.

**[The Python API guide](api/index.md)**: parsing and rendering MyST with Python.

**[](explain/index.md)**: background understanding and discussions of MyST markdown.
---
:header: bg-myst-three

**Get inspired**
^^^
**[Jupyter Book](https://jupyterbook.org)**: An open source project for building beautiful, publication-quality books and documents from computational material, built on top of the MyST Parser.

**[The Jupyter Book gallery](https://gallery.jupyterbook.org)**: examples of documents built with MyST.
:::

```{toctree}
:hidden:
sphinx/intro.md
```

```{toctree}
:caption: MyST Syntax
:hidden:
syntax/syntax
syntax/optional
syntax/reference
```

```{toctree}
:hidden:
:caption: Topic Guides
explain/index.md
sphinx/index.md
docutils.md
api/index.md
develop/index.md
```

```{toctree}
:hidden:
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
[rst-to-myst]: https://rst-to-myst.readthedocs.io
[mystyc]: https://mystyc.herokuapp.com
