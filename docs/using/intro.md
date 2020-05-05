# Getting Started

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

Or for package development:

```bash
git clone https://github.com/executablebooks/MyST-Parser
cd MyST-Parser
git checkout master
pip install -e .[sphinx,code_style,testing,rtd]
```

[pypi-badge]: https://img.shields.io/pypi/v/myst-parser.svg
[pypi-link]: https://pypi.org/project/myst-parser
[conda-badge]: https://anaconda.org/conda-forge/myst-parser/badges/version.svg
[conda-link]: https://anaconda.org/conda-forge/myst-parser

(parse-with-sphinx)=
## Parsing MyST with Sphinx

Sphinx is a documentation generator for building a website or book from multiple source documents and assets. To get started with Sphinx, see their [Quickstart Guide](https://www.sphinx-doc.org/en/master/usage/quickstart.html).

To use the MyST parser in Sphinx, simply add: `extensions = ["myst_parser"]` to your `conf.py` and all documents with the `.md` extension will be parsed as MyST.

Naturally this site is generated with Sphinx and MyST!

Some configuration options are also available using `myst_config` in your `conf.py`.
You can currently change the math bracket setting, and disable parsing of any of the syntax elements:

```python
extensions = ["myst_parser"]
myst_config = {"disable_syntax": ["emphasis"], "math_delimiters": "brackets"}
```

```md
*emphasis is now disabled*

\[a=1\]
```

```{seealso}
The {py:class}`~myst_parser.sphinx_parser.MystParser` class API
and
[markdown-it-py](https://github.com/executablebooks/markdown-it-py)
for the list of syntax elements (known as rules) that you can disable.
```

## Parsing Performance Benchmark

MyST-Parser uses the fastest, __*CommonMark compliant*__, parser written in python!

    $ myst-benchmark -n 50
    Test document: spec.md
    Test iterations: 50
    Running 6 test(s) ...
    =====================
    [mistune                (0.8.4):  5.52 s]*
    markdown-it-py          (0.2.3):  15.38 s
    myst-parser:sphinx      (0.8.0):  23.13 s
    mistletoe               (0.10.0): 16.92 s
    commonmark.py           (0.9.1):  35.61 s
    python-markdown:extra   (3.2.1):  66.89 s

As already noted by [mistletoe](https://github.com/miyuchina/mistletoe#performance),
although Mistune is the fastest of the parsers,
this is because it does not strictly follow the CommonMark spec,
which outlines a highly context-sensitive grammar for Markdown.
The simpler approach taken by Mistune  means that it cannot handle more
complex parsing cases, such as precedence of different types of tokens, escaping rules, etc.

The MyST parser is slightly slower than the base markdown-it-py parser, due to the additional syntax which it parses and the conversion to docutils AST,
but even then it is still comparably performant to the other parsers parser.
