(intro/get-started)=
# Get Started

This page describes how to get started with the MyST parser, with a focus on enabling it in the Sphinx documentation engine.

## Installation

[![PyPI][pypi-badge]][pypi-link]
[![Conda][conda-badge]][conda-link]

To install use [pip](https://pip.pypa.io):

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

(intro/sphinx)=
## Enable MyST in Sphinx

Sphinx is a documentation generator for building a website or book from multiple source documents and assets. To get started with Sphinx, see their [Quickstart Guide](https://www.sphinx-doc.org/en/master/usage/quickstart.html). This guide assumes that you've already got a pre-existing Sphinx site that builds properly.

To use the MyST parser in Sphinx, simply add the following to your `conf.py` file:

```python
extensions = ["myst_parser"]
```

This will activate the MyST Parser extension, causing all documents with the `.md` extension to be parsed as MyST.

:::{admonition} You can use both MyST and reStructuredText
:class: tip

Activating the MyST parser will simply *enable* parsing markdown files with MyST, and the rST parser that ships with Sphinx will still work the same way.
Files ending with `.md` will be parsed as MyST, and files ending in `.rst` will be parsed as reStructuredText.
:::

(intro/writing)=
## Write your first markdown document

Now that you've enabled the `myst-parser` in Sphinx, you can write MyST markdown in a file that ends with `.md` extension for your pages.

:::{note}
MyST markdown is a mixture of two flavors of markdown:

It supports all the syntax of **[CommonMark Markdown](https://commonmark.org/)** at its
base. This is a community standard flavor of markdown used across many projects.

In addition, it includes **[several extensions](../syntax/syntax.md) to CommonMark**.
These add extra syntax features for technical writing, such as the roles and directives used by Sphinx.
:::

To start off, create an empty file called `myfile.md` and give it a markdown title and text.

```md
# My nifty title

Some **text**!
```

In the "main document" of your Sphinx project (the landing page of your Sphinx documentation), include `myfile.md` in a `toctree` directive so that it is included in your documentation:

```rst
.. toctree::

   myfile.md
```

Now build your site:

```bash
make html
```

and navigate to your landing page.
You should see a link to the page generated from `myfile.md`.
Clicking that link should take you to your rendered Markdown!

## Extend markdown with a directive

The most important functionality available with MyST markdown is writing **directives**.
Directives are kind-of like functions that are designed for writing content.
Sphinx and reStructuredText use directives extensively.
Here's how a directive looks in MyST markdown:

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

For those who are familiar with reStructuredText, you can find [a mapping from MyST directive syntax to rST syntax here](syntax/directives).


As seen above, there are four main parts to consider when writing directives.

* **the directive name** is kind of like the function name. Different names trigger
  different functionality. They are wrapped in `{}` brackets.
* **directive arguments** come just after the directive name. They can be used
  to trigger behavior in the directive.
* **directive options** come just after the first line of the directive. They also
  control behavior of the directive.
* **directive content** is markdown that you put inside the directive. The directive
  often displays the content in a special way.

For example, add an **`admonition`** directive to your markdown page, like so:


````md
# My nifty title

Some **text**!

```{admonition} Here's my title
:class: warning

Here's my admonition content
```
````

Re-build your Sphinx site and you should see the new admonition box show up.

As you can see, we've used each of the four pieces described above to configure this
directive. Here's how the directive looks when rendered:

```{admonition} Here's my title
:class: warning

Here's my admonition content
```

:::{seealso}
For more information about using directives with MyST, see {ref}`syntax/directives`.
:::

(sphinx/intro:reference)=
## Reference a section label with a role

Roles are another core Sphinx tool. They behave similarly to directives, but are given
in-line with text instead of in a separate block. They have the following form:

```md
{rolename}`role content`
```

Roles are a bit more simple than directives, though some roles allow for more complex syntax inside their content area.
For example, the `ref` role is used to make references to other sections of your documentation, and allows you to specify the displayed text as well as the reference itself within the role:

```md
{ref}`My displayed text <my-ref>`
```

For example, let's add a **section reference** to your markdown file.
To do this, we'll first need to add a **label** to a section of your page.
To do so, use the following structure:

```md
(label-name)=
## Some header
```

Add this to your markdown file from above, like so:

````md
# My nifty title

Some **text**!

```{admonition} Here's my title
:class: warning

Here's my admonition content
```

(section-two)=
## Here's another section

And some more content.
````

Because your new section has a label (`section-two`), you can reference it with the `ref` role.
Add it to your markdown file like so:


```md
(label-name)=
## Some header
```

Add this to your markdown file from above, like so:

````md
# My nifty title

Some **text**!

```{admonition} Here's my title
:class: warning

Here's my admonition content
```

(section-two)=
## Here's another section

And some more content.

And here's {ref}`a reference to this section <section-two>`.
I can also reference the section {ref}`section-two` without specifying my title.
````

Re-build your documentation and you should see the references automatically inserted.
Here's an example of how the `ref` roles look in the final output:

Here's a reference to {ref}`sphinx/intro:reference`.

:::{seealso}
For more information about roles, see {ref}`syntax/roles`.
:::

## Add a comment using extra MyST syntax

There are many other kinds of syntax in MyST to make writing more productive and enjoyable.
Let's play around with a couple of options.

First, try writing a **comment**.
This can be done by adding a line starting with `%` to your markdown file.
For example, try adding a comment to your markdown file, like so:

````md
# My nifty title

Some **text**!

```{admonition} Here's my title
:class: warning

Here's my admonition content
```

(section-two)=
## Here's another section

And some more content.

% This comment won't make it into the outputs!
And here's {ref}`a reference to this section <section-two>`.
I can also reference the section {ref}`section-two` without specifying my title.
````

Re-build your documentation - the comment should _not_ be present in the output.

## Extending MyST via configuration

Thus far we have covered the basic MyST syntax with Sphinx.
However, there are a few ways that you can _extend_ this base syntax and get new functionality.
The first is to enable some "out of the box" extensions with the MyST parser.
These add new syntax that aren't part of "core MyST" but that are useful nonetheless (and may become part of core MyST one day).

Let's extend the base MyST syntax to enable **fences for directives**.
This allows you to define a directive with `:::` in addition to ` ``` `.
This is useful for directives that have markdown in their content.
By using `:::`, a non-MyST markdown renderer will still be able to render what is inside (instead of displaying it as a code block).

To activate extensions, add a list to your `conf.py` file that contains the extensions you'd like to activate.
For example, to activate the "colon code fences" extension, add the following to your `conf.py` file:

```python
myst_enable_extensions = [
  "colon_fence",
]
```

You may now use `:::` to define directives.
For example, modify your markdown file like so:

````md
# My nifty title

Some **text**!

```{admonition} Here's my title
:class: warning

Here's my admonition content
```

(section-two)=
## Here's another section

And some more content.

% This comment won't make it into the outputs!
And here's {ref}`a reference to this section <section-two>`.
I can also reference the section {ref}`section-two` without specifying my title.

:::{note}
And here's a note with a colon fence!
:::
````

It should render as a "note block" in your output when you build your site.

## Install a new Sphinx extension and use its functionality

The other way to extend MyST in Sphinx is to install Sphinx extensions that define new directives.
Directives are kind of like "functions" in Sphinx, and installing a new package can add new directives to use in your content.

For example, let's install the `sphinxcontib.mermaid` extension, which will allow us to generate [Mermaid diagrams](https://mermaid-js.github.io/mermaid/#/) with MyST.

First, install `sphinxcontrib.mermaid`:

```shell
pip install sphinxcontrib-mermaid
```

Next, add it to your list of extensions in `conf.py`:

```python
extensions = [
  "myst_parser",
  "sphinxcontrib.mermaid",
]
```

Now, add a **mermaid directive** to your markdown file.
For example:

````md
# My nifty title

Some **text**!

```{admonition} Here's my title
:class: warning

Here's my admonition content
```

(section-two)=
## Here's another section

And some more content.

% This comment won't make it into the outputs!
And here's {ref}`a reference to this section <section-two>`.
I can also reference the section {ref}`section-two` without specifying my title.

:::{note}
And here's a note with a colon fence!
:::

And finally, here's a cool mermaid diagram!

```{mermaid}
sequenceDiagram
  participant Alice
  participant Bob
  Alice->John: Hello John, how are you?
  loop Healthcheck
      John->John: Fight against hypochondria
  end
  Note right of John: Rational thoughts <br/>prevail...
  John-->Alice: Great!
  John->Bob: How about you?
  Bob-->John: Jolly good!
```
````

When you build your documentation, you should see something like this:

```{mermaid}
sequenceDiagram
  participant Alice
  participant Bob
  Alice->John: Hello John, how are you?
  loop Healthcheck
      John->John: Fight against hypochondria
  end
  Note right of John: Rational thoughts <br/>prevail...
  John-->Alice: Great!
  John->Bob: How about you?
  Bob-->John: Jolly good!
```

## Next steps - Learn more about MyST Syntax

In this tutorial we've covered some of the basics of MyST Markdown, how to enable and use it with Sphinx, and how to extend it for new use-cases.
There is much more functionality in MyST (and in the Sphinx ecosystem) that we haven't covered here.
For more information, see the [documentation on MyST Syntax](../syntax/syntax.md).
