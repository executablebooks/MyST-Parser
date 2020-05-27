# Getting Started

This page describes how to get started with the MyST parser, with a focus on enabling
it in the Sphinx documentation engine.

## Installation

[![PyPI][pypi-badge]][pypi-link]
[![Conda][conda-badge]][conda-link]

Installing the MyST parser provides access to two tools:

* A MyST-to-docutils parser and renderer.
* A Sphinx parser that utilizes the above tool in building your documenation.

To install the MyST parser, run the following in a
[Conda environment](https://docs.conda.io) (recommended):

```bash
conda install -c conda-forge myst-parser
```

or

```bash
pip install myst-parser[sphinx]
```

[pypi-badge]: https://img.shields.io/pypi/v/myst-parser.svg
[pypi-link]: https://pypi.org/project/myst-parser
[conda-badge]: https://anaconda.org/conda-forge/myst-parser/badges/version.svg
[conda-link]: https://anaconda.org/conda-forge/myst-parser

(parse-with-sphinx)=
## Enable MyST in Sphinx

Sphinx is a documentation generator for building a website or book from multiple source documents and assets. To get started with Sphinx, see their [Quickstart Guide](https://www.sphinx-doc.org/en/master/usage/quickstart.html).

To use the MyST parser in Sphinx, simply add: `extensions = ["myst_parser"]` to your `conf.py` and all documents with the `.md` extension will be parsed as MyST.

Naturally this site is generated with Sphinx and MyST!

## Writing MyST in Sphinx

Once you've enabled the `myst-parser` in Sphinx, it will be able to parser your MyST
markdown documents. This means that you can use the `.md` extension for your pages,
and write markdown in one of the following two flavors:

* [CommonMark Markdown](https://commonmark.org/) - the base flavor of markdown that is
  a standard across many communities.
* [MyST Markdown](syntax) - an extended flavor of CommonMark that includes syntax for
  Sphinx-specific functionality.

For example, you can include standard markdown like links: `[mylink](https://google.com)`
or MyST-specific syntax like roles: `` {myrole}`role content` ``.

For more information about the syntax that you can use with MyST markdown, see {doc}`syntax`.

```{tip}
Check out the [MyST-Markdown VS Code extension](https://marketplace.visualstudio.com/items?itemName=ExecutableBookProject.myst-highlight),
for MyST extended syntax highlighting.
```

## MyST configuration options

You can control the behavior of the MyST parser in Sphinx by modifying your `conf.py` file.
To do so, use the `myst_config` keyword with a dictionary of `key:val` pairs.

### Disable markdown syntax for the parser

If you'd like to either enable or disable custom markdown syntax, you may do so like so:

```python
myst_config = {
    "disable_syntax": ["list", "of", "disabled", "elements"]
}
```

Anything in this list will no longer be parsed by the MyST parser.

For example, to disable the `emphasis` in-line syntax, use this configuration:

```python
myst_config = {
    "disable_syntax": ["emphasis"]
}
```

emphasis syntax will now be disabled. For example, the following will be rendered
*without* any italics:

```md
*emphasis is now disabled*
```

For a list of all the syntax elements you can disable, see the
[`markdown-it-py` documentation](https://markdown-it-py.readthedocs.io/en/latest/using.html).


### Use bracket delimiters for math

You can also change the delimiters that are used for mathematics. By default, these
are **dollar signs (`$`)**. For example, to use brackets instead of dollar signs, use
this configuration:

```python
myst_config = {
    "math_delimiters": "brackets"
}
```

This will tell the MyST parser to treat the following as math:

```md
\[a=1\]
```

```{seealso}
The {py:class}`~myst_parser.sphinx_parser.MystParser` class API
and
[markdown-it-py](https://github.com/executablebooks/markdown-it-py)
for the list of syntax elements (known as rules) that you can disable.
```
