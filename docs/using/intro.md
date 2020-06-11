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

## How does MyST parser relate to Sphinx?

The Sphinx documentation engine supports a number of different input types. By default,
it reads **reStructuredText** (`.rst`) files. Sphinx uses a **parser** to parse input files
into its own internal document model (which is provided by a core Python project,
[docutils](https://docutils.sourceforge.io/)).

Developers can *extend Sphinx* to support other kinds of input files. Any content file
can be read into the Sphinx document structure, provided that somebody writes a
**parser** for that file. Once a content file has been parsed into Sphinx, it behaves
nearly the same way as any other content file, regardless of the language in which it
was written.

The MyST-parser is a Sphinx parser for the MyST markdown language. When you use it,
Sphinx will know how to parse content files that contain MyST markdown (by default,
Sphinx will assume any files ending in `.md` are written in MyST markdown).

```{note}
Sphinx will still be able to parse files written in `.rst`. Activating this parser
simply adds another parser, and Sphinx will still be able to use its default parser
for `.rst` files.
```

(intro/writing)=
## Writing MyST in Sphinx

Once you've enabled the `myst-parser` in Sphinx, it will be able to parse your MyST
markdown documents. This means that you can use the `.md` extension for your pages,
and write MyST markdown in these pages.

```{tip}
MyST markdown is a mixture of two flavors of markdown:

It supports all the syntax of **[CommonMark Markdown](https://commonmark.org/)** at its
base. This is a community standard flavor of markdown used across many projects.

In addition, it includes **several extensions to CommonMark**
(often described as [MyST Markdown syntax](syntax)). These add extra syntax features
designed to work with the Sphinx ecosystem (and inspired by reStructuredText)
```

The following sections cover a few core syntax patterns in MyST markdown, you can
find a more exhaustive list in {doc}`syntax`.

### Block-level directives with MyST markdown

The most important functionality available with MyST markdown is writing **directives**.
Directives are kind-of like functions that are designed for writing content. Sphinx
and reStructuredText use directives extensively. Here's how a directive looks in
MyST markdown:

````{margin} Alternative options syntax
If you've got a lot of options for your directive, or have a value that is really
long (e.g., that spans multiple lines), then you can also wrap your options in
`---` lines and write them as YAML. For example:

```yaml
---
key1: val1
key2: |
  val line 1
  val line 2
---
```
````

````
```{directivename} <directive arguments>
:optionname: <valuename>

<directive content>
```
````

````{admonition} MyST vs. rST
:class: warning
For those who are familiar with reStructuredText, here is the equivalent in rST:

```rst
.. directivename: <directive-arguments>
  :optionname: <valuename>

  <directive content>
```

Note that almost all documentation in the Sphinx ecosystem is written with
reStructuredText (MyST is only a few months old). That means you'll likely see examples
that have rST structure. You can modify any rST to work with MyST. Use this page,
and [the syntax page](syntax) to help guide you.
````

As seen above, there are four main parts to consider when writing directives.

* **the directive name** is kind of like the function name. Different names trigger
  different functionality. They are wrapped in `{}` brackets.
* **directive arguments** come just after the directive name. They can be used
  to trigger behavior in the directive.
* **directive options** come just after the first line of the directive. They also
  control behavior of the directive.
* **directive content** is markdown that you put inside the directive. The directive
  often displays the content in a special way.

For example, here's an **`admonition`** directive:

````
```{admonition} Here's my title
:class: warning

Here's my admonition content
```
````

As you can see, we've used each of the four pieces described above to configure this
directive. Here's how it looks when rendered:

```{admonition} Here's my title
:class: warning

Here's my admonition content
```

For more information about using directives with MyST, see {ref}`syntax/directives`.

### In-line roles with MyST Markdown

Roles are another core Sphinx tool. They behave similarly to directives, but are given
in-line with text instead of in a separate block. They have the following form:

```
{rolename}`role content`
```

For those who are familiar with reStructuredText, here is the equivalent in rST:

```rst
:rolename:`role content`
```

As you can see, roles are a bit more simple than directives, though some roles allow
for more complex syntax inside their content area. For example, the `ref` role is used
to make references to other sections of your documentation, and allows you to specify
the displayed text as well as the reference itself within the role:

```
{ref}`My displayed text <my-ref>`
```

For example, the following reference role: `` {ref}`Check out this reference <syntax/roles>` ``
will be rendered as {ref}`Check out this reference <syntax/roles>`.

For more information about roles, see {ref}`syntax/roles`.

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
