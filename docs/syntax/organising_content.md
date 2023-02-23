
(organising-content)=
# Organising content

Sphinx allows you to organise your content into multiple documents, and to include content from other documents.

This section describes how to do this with MyST Markdown.

(hiya)=
## Document structure

Single MyST Markdown documents are structured using [headings](typography.md#headings).

All headings at the root level of the document are included in the Table of Contents (ToC) for that page.

Many HTML themes will already include this ToC in a sidebar, but you can also include it in the main content of the page using the contents {{directive}}:

:::{myst-example}
```{contents} Table of Contents
:depth: 3
```
:::

Options:

:depth: Can be used to specify the depth of the ToC.
:local: Can be used to only include headings in the current section of the document.
:backlinks: Can be used to include a link to the ToC at the end of each section.
:class: Is available to add a custom CSS class to the ToC.

:::::{warning}

Because the structure of the document is determined by the headings, it is problematic to have "non-consecutive" headings in a document, such as:

```md
# Heading 1
### Heading 3
```

If you wish to include such a heading, you can use the [attrs_block](#syntax/attributes/block) extension to wrap the heading in a `div`, so that it is not included in the ToC:

```md
# Heading 1
:::
### Heading 3
:::
```

:::::


:::::{admonition} Setting a title in front-matter
:class: tip dropdown

```{versionadded} 0.17.0
```

The `myst_title_to_header = True`{l=python} [configuration](#sphinx/config-options)
allows for a `title` key to be present in the [document front matter](#syntax/frontmatter).

This will then be used as the document's header (parsed as Markdown).
For example:

```md
---
title: My Title with *emphasis*
---
```

would be equivalent to:

```md
# My Title with *emphasis*
```

:::::

(organising-content/include)=
## Inserting other documents directly into the current document

The `include` directive allows you to insert the contents of another document directly into the flow of the current document.

:::{seealso}
The [`literalinclude` directive](#syntax/literalinclude), for including source code from files.
:::

:::{myst-example}
```{literalinclude} example.txt
```

```{include} example.txt
```
:::

The following options allow you to include only part of a document:

:start-line: Only the content starting from this line number will be included (numbering starts at 1, and negative count from the end)
:end-line: Only the content up to (but excluding) this line will be included.
:start-after: Only the content after the first occurrence of the specified text will be included.
:end-before: Only the content before the first occurrence of the specified text (but after any after text) will be included.

:::{myst-example}
```{literalinclude} example.txt
```

```{include} example.txt
:start-line: 1
:end-line: 2
```

```{include} example.txt
:start-after: Hallo
:end-before: you!
```
:::

The following options allow you to modify the content of the included document,
to make it relative to the location that it is being inserted:

:heading-offset: Offset all the heading levels by this positive integer, e.g. changing `#` to `####`
:relative-docs: Make Markdown file references, relative to the current document, if they start with a certain prefix
:relative-images: Make Markdown image references, relative to the current document

:::{myst-example}
```{literalinclude} examples/example_relative_include.txt
```

```{include} examples/example_relative_include.txt
:heading-offset: 3
:relative-docs: ..
:relative-images:
```
:::

Additional options:
:encoding: The text encoding of the external file

::::{admonition} Including to/from reStructuredText files
:class: tip dropdown

As explained in [this section](#syntax/directives/parsing), all MyST directives will parse their content as Markdown.
So to include rST, we must first "wrap" the directive in the [eval-rst directive](#syntax/directives/parsing):

:::{myst-example}
```{eval-rst}
.. include:: ../faq/snippets/include-rst.rst
```
:::

To include a MyST file within a ReStructuredText file, we can use the `parser` option of the `include` directive:

```rst
.. include:: include.md
   :parser: myst_parser.sphinx_
```

:::{important}
The `parser` option requires `docutils>=0.17`
:::

::::

(syntax/toctree)=
## Using `toctree` to include other documents as children

To structure a project, with multiple documents, the [toctree directive](inv:sphinx:*:directive#toctree) is utilised.

The designate documents as children of the current document,
building up a nested hierarchy of documents starting from a [`root_doc`](inv:sphinx:*:confval#root_doc).

:::{myst-example}
```{toctree}
examples/content_child1.md
examples/content_child2.md
```
:::

The `toctree` has options:

:glob: Indicates that all entries are then matched against the list of available documents,
    and matches are inserted into the list alphabetically

The following options to control how it is displayed within the document:

:caption: A title for this toctree
:hidden: Do not show within the document
:includehidden: Included child hidden `toctree` entries
:maxdepth: The depth of document sub-headings shown
:titlesonly: Only show the first top-level heading
:reversed: Reverse the order of the entries in the list

Additional options:

:name: Allow the `toctree` to be referenced
:numbered: Number all headings in children. If an integer is specified, then this is the depth to number down to

:::{tip}
Sub-toctrees are automatically numbered, so don’t give the `:numbered:` flag to those
:::
