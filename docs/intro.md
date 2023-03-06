(intro/get-started)=
# 🚀 Get Started

This page gives a quick overview of how to get started with MyST Markdown, and how to use it within Docutils and Sphinx.

## Installation

[![PyPI][pypi-badge]][pypi-link]
[![Conda][conda-badge]][conda-link]

To install myst-parser use [pip](https://pip.pypa.io):

```bash
pip install myst-parser
```

or [Conda](https://docs.conda.io):

```bash
conda install -c conda-forge myst-parser
```

[pypi-badge]: https://img.shields.io/pypi/v/myst-parser.svg
[pypi-link]: https://pypi.org/project/myst-parser
[conda-badge]: https://anaconda.org/conda-forge/myst-parser/badges/version.svg
[conda-link]: https://anaconda.org/conda-forge/myst-parser

(intro/writing)=
## Write a Markdown document

To start off, create an empty file called `example.md` and give it a Markdown title and text.
We can now use the `myst-docutils-demo` [CLI tool](docutils.md), from the installed package, to parse this file to HTML:

:::{myst-to-html}
# My nifty title

Some **text**!
:::

## Extend Markdown with MyST syntax

MyST is an extension of [CommonMark Markdown](https://commonmark.org/),
that includes a rich [additional syntax](syntax/typography.md) for technical authoring,
and can integrate with Docutils and Sphinx.

For example, MyST includes {{role}} and {{directive}} extensions points, to allow for richer features, such as [admonitions](syntax/admonitions.md) and [figures](syntax/images_and_figures.md).

Lets add an `admonition` directive and `sup` role to your Markdown page, like so:


::::{myst-to-html}
:extensions: colon_fence

# My nifty title

Some **text**!

:::{admonition} Here's my title
:class: tip

Here's my admonition content.{sup}`1`
:::

::::

:::{tip}
MyST works with just about all Docutils and Sphinx roles and directives.

Note, Sphinx provides a superset of the Docutils roles and directives, so some may not work in the Docutils CLI.
:::

(intro/reference)=
## Cross-referencing

MyST-Parser offers powerful [cross-referencing features](syntax/cross-referencing.md), to link to documents, headers, figures and more.

For example, to add a section *reference target*, and reference it:

::::{myst-to-html}
(header-label)=
# A header

[My reference](#header-label)
::::

(intro/sphinx)=
## Enable MyST in Sphinx

To get started with Sphinx, see their [quick-start guide](inv:sphinx#usage/quickstart).

To use the MyST parser in Sphinx, simply add the following to your `conf.py` [configuration file](inv:sphinx#usage/configuration):

```python
extensions = ["myst_parser"]
```

This will activate the MyST Parser extension, causing all documents with the `.md` extension to be parsed as MyST.

Our `example.md` file can now be added as the [index page](inv:sphinx#usage/index),
or see the [organising content section](#syntax/toctree) about creating `toctree` directives, to add `example.md` to.

:::{tip}
There are a range of great HTML themes that work well with MyST, such as [sphinx-book-theme](https://github.com/executablebooks/sphinx-book-theme) (used here),
[pydata-sphinx-theme](https://github.com/pydata/pydata-sphinx-theme/) and
[furo](https://github.com/pradyunsg/furo)
:::

## Configuring MyST-Parser

The <project:configuration.md> section contains a complete list of configuration options for the MyST-Parser.

These can be applied globally, e.g. in the sphinx `conf.py`:

```python
myst_enable_extensions = ["colon_fence"]
```

Or they can be applied to specific documents, at the top of the document, in frontmatter:

```yaml
---
myst:
  enable_extensions: ["colon_fence"]
---
```

## Extending Sphinx

The other way to extend MyST in Sphinx is to install Sphinx extensions that define new roles, directives, etc.

For example, let's install the [sphinx-design](https://github.com/executablebooks/sphinx-design) extension, which will allow us to create beautiful, screen-size responsive web-components.

First, install `sphinx-design`:

```shell
pip install sphinx-design
```

Next, add it to your list of extensions in `conf.py`:

```python
extensions = [
  "myst_parser",
  "sphinx_design",
]
```

Now, we can use the `design` directive to add a web-component to our Markdown file!

::::{myst-example}
:::{card} Card Title
Header
^^^
Card content
+++
Footer
:::
::::


::::::{myst-example}

::::{tab-set}

:::{tab-item} Label1
Content 1
:::

:::{tab-item} Label2
Content 2
:::

::::

::::::

% TODO this can uncommented once https://github.com/mgaitan/sphinxcontrib-mermaid/issues/109 is fixed
% For example, let's install the `sphinxcontrib.mermaid` extension,
% which will allow us to generate [Mermaid diagrams](https://mermaid-js.github.io/mermaid/#/) with MyST.

% First, install `sphinxcontrib.mermaid`:

% ```shell
% pip install sphinxcontrib-mermaid
% ```

% Next, add it to your list of extensions in `conf.py`:

% ```python
% extensions = [
%   "myst_parser",
%   "sphinxcontrib.mermaid",
% ]
% ```

% Now, add a **mermaid directive** to your Markdown file.
% For example:

% :::{myst-example}
% Here's a cool mermaid diagram!
%
% ```{mermaid}
% sequenceDiagram
%   participant Alice
%   participant Bob
%   Alice->John: Hello John, how are you?
%   loop Healthcheck
%       John->John: Fight against hypochondria
%   end
%   Note right of John: Rational thoughts <br/>prevail...
%   John-->Alice: Great!
%   John->Bob: How about you?
%   Bob-->John: Jolly good!
% ```
% :::


There are many other great Sphinx extensions that work with MyST, such as the ones used in this documentation:

:sphinx-design: Add beautiful, responsive web-components to your documentation
:sphinx-copybutton: Add a copy button to your code blocks
:sphinxext-rediraffe: Add redirects to your documentation
:sphinxext-opengraph: Add OpenGraph metadata to your documentation
:sphinx-pyscript: Execute Python code in your documentation, [see here](https://github.com/sphinx-extensions2/sphinx-pyscript)
:sphinx-tippy: Add tooltips to your documentation, [see here](https://github.com/sphinx-extensions2/sphinx-tippy)
:sphinx-autodoc2: Generate documentation from docstrings, [see here](https://github.com/sphinx-extensions2/sphinx-autodoc2)
:sphinx-togglebutton: Add collapsible content to your documentation
:sphinxcontrib.mermaid: Generate [Mermaid diagrams](https://mermaid-js.github.io/mermaid/#/)


:::{seealso}
[sphinx-extensions](https://sphinx-extensions.readthedocs.io/en/latest/),
for a curated and opinionated list of Sphinx extensions.
:::
