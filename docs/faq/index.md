(myst-sphinx)=

# FAQ

## How-tos

These sections describe some common scenarios and use-cases for writing MyST with Sphinx.

(howto/include-rst)=
### Include rST files into a Markdown file

As explained in [this section](#syntax/directives/parsing), all MyST directives will parse their content as Markdown.
Therefore, using the conventional `include` directive, will parse the file contents as Markdown:

````md
```{include} snippets/include-md.md
```
````

```{include} snippets/include-md.md
```

To include rST, we must first "wrap" the directive in the [eval-rst directive](#syntax/directives/parsing):

````md
```{eval-rst}
.. include:: snippets/include-rst.rst
```
````

```{eval-rst}
.. include:: snippets/include-rst.rst
```

(howto/include-md)=
### Include Markdown files into an rST file

To include a MyST file within a ReStructuredText file, we can use the `parser` option of the `include` directive:

```rst
.. include:: include.md
   :parser: myst_parser.sphinx_
```

```{important}
The `parser` option requires `docutils>=0.17`
```

### Use MyST in Jupyter Notebooks

The [MyST-NB](https://myst-nb.readthedocs.io) tool provides a Sphinx extension for parsing **Jupyter Notebooks written with MyST Markdown**. It includes features like automatically executing notebooks during documentation builds, storing notebook cell outputs in order to insert them elsewhere in your documentation, and more. See the [MyST-NB documentation](https://myst-nb.readthedocs.io) for more information.

(howto/include-readme)=
### Include a file from outside the docs folder (like README.md)

:::{seealso}
<project:#organising-content/include>
:::

You can include a file, including one from outside the project using e.g.:

````md
```{include} ../README.md
```
````

**However**, including a file will not usually resolve local links correctly, like `![](my-image.png)`, since it treats the text as if it originated from the "including file".

As of myst-parser version 0.12.7, a new, experimental feature has been added to resolve such links.
You can now use for example:

````md
Source:
```{literalinclude} ../../example.md
:language: md
```
Included:
```{include} ../../example.md
:relative-docs: docs/
:relative-images:
```
````

Source:

```{literalinclude} ../../example-include.md
:language: md
```

Included:

```{include} ../../example-include.md
:relative-docs: docs/
:relative-images:
```

The include here attempts to re-write local links, to reference them from the correct location!
The `relative-docs` must be given the prefix of any links to re-write, to distinguish them from sphinx cross-references.

:::{important}
The current functionality only works for Markdown style images and links.

If you encounter any issues with this feature, please don't hesitate to report it.
:::

(howto/autodoc)=
### Use `sphinx.ext.autodoc` in Markdown files

See [](#syntax/apis) for this information.

(howto/autosectionlabel)=
### Automatically create targets for section headers

:::{versionadded} 0.13.0
See [](#syntax/implicit-targets) for this information.
:::


### Suppress warnings

See <project:#myst-warnings> for this information.

### Sphinx-specific page front matter

Sphinx intercepts front matter and stores them within the global environment
(as discussed in the [sphinx documentation](inv:sphinx#usage/*/field-lists)).
There are certain front-matter keys (or their translations) that are also recognised specifically by docutils and parsed to inline Markdown:

- `author`
- `authors`
- `organization`
- `address`
- `contact`
- `version`
- `revision`
- `status`
- `date`
- `copyright`
- `dedication`
- `abstract`

A classic use-case is to specify 'orphan' documents, that are not specified in any toctrees.
For example, inserting the following syntax at the top of a page will cause Sphinx to treat it as an orphan page:

```md
---
orphan: true
---

This is an orphan document, not specified in any toctrees.
```

### Migrate pre-existing rST into MyST

If you've already got some reStructuredText files that you'd like to convert into MyST Markdown, try the [`rst-to-myst`](https://github.com/executablebooks/rst-to-myst) tool, which allows you to convert single rST files to MyST markdown documents.

## Disable Markdown syntax for the parser

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

For a list of all the syntax elements you can disable, see the [markdown-it parser guide](inv:markdown_it#using).

## Common errors and questions

These are common issues and gotchas that people may experience when using the MyST Sphinx extension.

### What markup language should I use inside directives?

If you need to parse content *inside* of another block of content (for example, the
content inside a **note directive**), note that the MyST parser will be used for this
nested parsing as well.

### Why doesn't my role/directive recognize markdown link syntax?

There are some roles/directives that _hard-code_ syntax into
their behavior. For example, many roles allow you to supply titles for links like so:
`` {role}`My title <myref>` ``. While this looks like reStructuredText, the role may
be explicitly expecting the `My title <myref>` structure, and so MyST will behave the same way.
