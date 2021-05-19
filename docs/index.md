# MyST - Markedly Structured Text <img src="_static/logo-square.svg" width=40 />

[![PyPI][pypi-badge]][pypi-link]
[![Conda][conda-badge]][conda-link]

**MyST is a rich and extensible flavor of Markdown meant for technical documentation and publishing**.

MyST is a flavor of markdown that is designed for simplicity, flexibility, and extensibility.
Here are a few key features of MyST Markdown:

{fa}`check,text-success mr-1` It is [a superset of CommonMark markdown][commonmark].
: Any CommonMark document is also MyST-compliant.

{fa}`check,text-success mr-1` It [extends CommonMark with rich writing syntax](extended-block-tokens).
: These make it easier to write MyST and extend its functionality to technical documentation (for example, line commenting and footnotes).

{fa}`check,text-success mr-1` It provides [extension points with directives and roles](syntax/directives).
: Any MyST parser can define new functionality via a standard syntax extension point (this is kind of like defining functions with markdown).

This MyST Parser serves as a reference implementation for MyST Markdown, and comes bundled with several tools that help you use MyST in your work.
It comes bundled with a few tools to help you use MyST with Python:

[A Python parser of MyST markdown](api/index)
: This can be extended to add new functionality and outputs for MyST, and is built on top of [`markdown-it-py`](https://markdown-it-py.readthedocs.io/).

[A markdown parser for Sphinx](sphinx/index)
: You can write your entire {doc}`Sphinx documentation <sphinx:usage/quickstart>` in Markdown, including [**roles** and **directives**](syntax/directives).
  This allows you to extend MyST's functionality in Sphinx via Sphinx extensions.

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
sphinx/index.md
api/index.md
explain/index.md
```

## About the project

These sections cover "meta" information about the MyST Markdown project.

```{toctree}
:maxdepth: 2
:caption: About the project
examples/index.md
develop/index.md
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
