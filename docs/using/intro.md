(intro/get-started)=
# Getting Started

This page describes how to get started with the MyST parser, with a focus on enabling
it in the Sphinx documentation engine.

## Installation

[![PyPI][pypi-badge]][pypi-link]
[![Conda][conda-badge]][conda-link]

Installing the MyST parser provides access to two tools:

* A MyST-to-docutils parser and renderer.
* A Sphinx parser that utilizes the above tool in building your documentation.

To install the MyST parser, run the following in a
[Conda environment](https://docs.conda.io) (recommended):

```bash
conda install -c conda-forge myst-parser
```

or

```bash
pip install myst-parser
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

:::{admonition} You can use both MyST and reStructuredText
:class: tip

Activating the MyST parser will simply *enable* parsing markdown files with MyST, and the rST parser that ships with Sphinx by default will still work the same way.
You can have combinations of both markdown and rST files in your documentation, and Sphinx will choose the right parser based on each file's extension.
Sphinx features like cross-references will work just fine between the pages.

You can even inject raw rST into Markdown files! (see [this explanation](syntax/directives/parsing))
:::

:::{admonition} Want to add Jupyter Notebooks to your documentation?
:class: seealso

See also [MyST-NB](https://myst-nb.readthedocs.io), our complimentary parser and execution engine,
for ipynb and text-based notebooks.
:::

## How does MyST parser relate to Sphinx?

The Sphinx documentation engine supports a number of different input types. By default,
Sphinx reads **reStructuredText** (`.rst`) files. Sphinx uses a **parser** to parse input files
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

:::{note}
Sphinx will still be able to parse files written in `.rst`. Activating this parser
simply adds another parser, and Sphinx will still be able to use its default parser
for `.rst` files.
:::

(intro/writing)=
## Writing MyST in Sphinx

Once you've enabled the `myst-parser` in Sphinx, it will be able to parse your MyST
markdown documents. This means that you can use the `.md` extension for your pages,
and write MyST markdown in these pages.

:::{note}
MyST markdown is a mixture of two flavors of markdown:

It supports all the syntax of **[CommonMark Markdown](https://commonmark.org/)** at its
base. This is a community standard flavor of markdown used across many projects.

In addition, it includes **several extensions to CommonMark**
(often described as [MyST Markdown syntax](syntax)). These add extra syntax features
designed to work with the Sphinx ecosystem (and inspired by reStructuredText)
:::

:::{tip}
If you want to parse your files as only **strict** CommonMark (no extensions), then you can set the `conf.py` option `myst_commonmark_only=True`.
:::

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
reStructuredText (MyST is only a few months old).
That means you'll likely see examples that have rST structure. You can modify any rST to work with MyST. Use this page, and [the syntax page](./syntax.md) to help guide you.
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

```md
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

```md
{ref}`My displayed text <my-ref>`
```

For example, the following reference role: `` {ref}`Check out this reference <syntax/roles>` ``
will be rendered as {ref}`Check out this reference <syntax/roles>`.

For more information about roles, see {ref}`syntax/roles`.

:::{tip}
Check out the [MyST-Markdown VS Code extension](https://marketplace.visualstudio.com/items?itemName=ExecutableBookProject.myst-highlight),
for MyST extended syntax highlighting.
:::

(intro/config-options)=
## MyST configuration options

You can control the behaviour of the MyST parser in Sphinx by modifying your `conf.py` file.
To do so, use the keywords beginning `myst_`.

`````{list-table}
:header-rows: 1

* - Option
  - Default
  - Description
* - `myst_commonmark_only`
  - `False`
  - If `True` convert text as strict CommonMark (all options below are then ignored)
* - `myst_disable_syntax`
  - ()
  - List of markdown syntax elements to disable, see the [markdown-it parser guide](markdown_it:using).
* - `enable_extensions`
  - `["dollarmath"]`
  - Enable Markdown extensions, [see here](syntax-optional) for details.
* - `myst_url_schemes`
  - `None`
  - [URI schemes](https://en.wikipedia.org/wiki/List_of_URI_schemes) that will be recognised as external URLs in `[](scheme:loc)` syntax, or set `None` to recognise all.
    Other links will be resolved as internal cross-references.
* - `myst_heading_anchors`
  - `None`
  - Enable auto-generated heading anchors, up to a maximum level, [see here](syntax/header-anchors) for details.
`````

List of extensions:

- "amsmath": enable direct parsing of [amsmath](https://ctan.org/pkg/amsmath) LaTeX equations
- "colon_fence": Enable code fences using `:::` delimiters, [see here](syntax/colon_fence) for details
- "deflist"
- "dollarmath": Enable parsing of dollar `$` and `$$` encapsulated math
- "html_image": Convert HTML `<img>` elements to sphinx image nodes, see the [image syntax](syntax/images) for details
- "linkify": automatically identify "bare" web URLs and add hyperlinks
- "replacements": automatically convert some common typographic texts
- "smartquotes": automatically convert standard quotations to their opening/closing variants
- "substitution": substitute keys

Math specific, when `"dollarmath"` activated, see the [Math syntax](syntax/math) for more details:

`````{list-table}
:header-rows: 1

* - Option
  - Default
  - Description
* - `myst_dmath_allow_labels`
  - `True`
  - Parse `$$...$$ (label)` syntax (if dmath enabled)
* - `myst_dmath_allow_space`
  - `True`
  - If False then inline math will only be parsed if there are no initial/final spaces,
    e.g. `$a$` but not `$ a$` or `$a $`
* - `myst_dmath_allow_digits`
  - `True`
  - If False then inline math will only be parsed if there are no initial/final digits,
    e.g. `$a$` but not `1$a$` or `$a$2` (this is useful for using `$` as currency)
* - `myst_amsmath_enable`
  - `False`
  - Enable direct parsing of [amsmath LaTeX environments](https://ctan.org/pkg/amsmath)
* - `myst_update_mathjax`
  - `True`
  - If using [sphinx.ext.mathjax](https://www.sphinx-doc.org/en/master/usage/extensions/math.html#module-sphinx.ext.mathjax) (the default) then `mathjax_config` will be updated,
  to ignore `$` delimiters and LaTeX environments, which should instead be handled by
  `myst_dmath_enable` and `myst_amsmath_enable` respectively.
`````

### Disable markdown syntax for the parser

If you'd like to either enable or disable custom markdown syntax, use `myst_disable_syntax`.
Anything in this list will no longer be parsed by the MyST parser.

For example, to disable the `emphasis` in-line syntax, use this configuration:

```python
myst_disable_syntax = ["emphasis"]
```

emphasis syntax will now be disabled. For example, the following will be rendered
*without* any italics:

```md
*emphasis is now disabled*
```

For a list of all the syntax elements you can disable, see the [markdown-it parser guide](markdown_it:using).
