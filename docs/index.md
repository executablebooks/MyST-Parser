---
sd_hide_title: true
---

# 🔎 Overview

::::{grid}
:reverse:
:gutter: 3 4 4 4
:margin: 1 2 1 2

:::{grid-item}
:columns: 12 4 4 4

```{image} _static/logo-square.svg
:width: 200px
:class: sd-m-auto
:name: landing-page-logo
```

:::

:::{grid-item}
:columns: 12 8 8 8
:child-align: justify
:class: sd-fs-5

```{rubric} MyST - Markedly Structured Text - Parser
```

A Sphinx and Docutils extension to parse MyST,
a rich and extensible flavour of Markdown for authoring technical and scientific documentation.

````{div} sd-d-flex-row
```{button-ref} intro
:ref-type: doc
:color: primary
:class: sd-rounded-pill sd-mr-3

Get Started
```

```{button-ref} live-preview
:ref-type: doc
:color: secondary
:class: sd-rounded-pill

Live Demo
```
````

:::

::::

---

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`markdown;1.5em;sd-mr-1` CommonMark-plus
:link: syntax/core
:link-type: ref

MyST extends the CommonMark syntax specification, to support technical authoring features such as tables and footnotes.

+++
[Learn more »](syntax/core)
:::

:::{grid-item-card} {octicon}`plug;1.5em;sd-mr-1` Sphinx compatible
:link: roles-directives
:link-type: ref

Use the MyST role and directive syntax to harness the full capability of Sphinx, such as admonitions and figures, and all existing Sphinx extensions.

+++
[Learn more »](roles-directives)
:::

:::{grid-item-card} {octicon}`tools;1.5em;sd-mr-1` Highly configurable
:link: configuration
:link-type: doc

MyST-parser can be configured at both the global and individual document level,
to modify parsing behaviour and access extended syntax features.

+++
[Learn more »](configuration)
:::

::::

---

```{rubric} Additional resources
```

[MyST-Markdown VS Code extension](https://marketplace.visualstudio.com/items?itemName=ExecutableBookProject.myst-highlight)
: For MyST extended syntax highlighting and authoring tools.

[Convert existing ReStructuredText files to Markdown][rst-to-myst]
: Use the [rst-to-myst] CLI or [the MySTyc interactive web interface](https://astrojuanlu.github.io/mystyc/).

[MyST-NB](https://myst-nb.readthedocs.io)
: A Sphinx and Docutils extension for compiling Jupyter Notebooks into high quality documentation formats, built on top of the MyST-Parser.

[Jupyter Book](https://jupyterbook.org)
: An open source project for building beautiful, publication-quality books and documents from computational material, built on top of the MyST-Parser and MyST-NB.

[The Jupyter Book gallery](https://executablebooks.org/en/latest/gallery.html)
: Examples of documents built with MyST.

[Javascript MyST parser][mystjs]
: The [mystjs] Javascript parser, allows you to parse MyST in websites.

[markdown-it-py]
: A CommonMark-compliant and extensible Markdown parser, used by MyST-Parser to parse source text to tokens.

```{rubric} Acknowledgements
```

The MyST markdown language and MyST parser are both supported by the open community,
[The Executable Book Project](https://executablebooks.org).

```{toctree}
:hidden:
intro.md
live-preview.md
```

```{toctree}
:hidden:
:caption: ✏️ Authoring

syntax/typography.md
syntax/admonitions.md
syntax/images_and_figures.md
syntax/tables.md
syntax/code_and_apis.md
syntax/cross-referencing.md
syntax/math.md
```

```{toctree}
:hidden:
:caption: 📚 Guides

configuration.md
syntax/organising_content.md
syntax/optional
syntax/roles-and-directives.md
docutils.md
faq/index.md
```

```{toctree}
:hidden:
:caption: 📖 Reference

develop/_changelog.md
develop/index.md
syntax/reference
develop/background.md
apidocs/index.rst
```

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
[markdown-it]: https://markdown-it.github.io/
[rst-to-myst]: https://rst-to-myst.readthedocs.io
[mystjs]: https://github.com/executablebooks/mystjs
