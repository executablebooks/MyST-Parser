# Background

These sections discuss high-level questions about the MyST ecosystem, and explain a few decisions made in the project.

## Why did we create MyST markdown?

While markdown is ubiquitous, it is not powerful enough for writing modern,
fully-featured documentation. Some flavors of markdown support features needed for this,
but there is no community standard around various syntactic choices for these features.

Sphinx is a documentation generation framework written in Python. It heavily-utilizes
reStructuredText syntax, which is another markup language for writing documents. In
particular, Sphinx defines two extension points that are extremely useful:
**{ref}`in-line roles<sphinx:rst-roles-alt>`** and **{ref}`block-level directives <sphinx:rst-directives>`**.

**This project is an attempt at combining the simplicity and readability of Markdown
with the power and flexibility of reStructuredText and the Sphinx platform.** It
starts with the [CommonMark markdown specification][commonmark], and selectively adds a few extra
syntax pieces to utilize the most powerful parts of reStructuredText.

```{note}
The CommonMark community has been discussing an "official" extension syntax for many
years now (for example, see
[this seven-year-old thread about directives](https://talk.commonmark.org/t/generic-directives-plugins-syntax/444) as well as
[this more recent converstaion](https://talk.commonmark.org/t/support-for-extension-token/2771),
and [this comment listing several more threads on this topic](https://talk.commonmark.org/t/extension-terminology-and-rules/1233)).

We have chosen a "roles and directives" syntax that seems reasonable and follows other
common conventions in Markdown flavors. However, if the CommonMark community ever
decides on an "official" extension syntax, we will likely utilize this syntax for
MyST.
```

## The relationship between MyST, reStructuredText, and Sphinx

MyST markdown provides a markdown equivalent of the reStructuredText syntax,
meaning that you can do anything in MyST that you can do with reStructuredText.

The Sphinx documentation engine supports a number of different input types. By default,
Sphinx reads **reStructuredText** (`.rst`) files. Sphinx uses a **parser** to parse input files
into its own internal document model (which is provided by a core Python project,
[docutils](https://docutils.sourceforge.io/)).

Developers can *extend Sphinx* to support other kinds of input files. Any content file
can be read into the Sphinx document structure, provided that somebody writes a
**parser** for that file. Once a content file has been parsed into Sphinx, it behaves
nearly the same way as any other content file, regardless of the language in which it
was written.

The MyST-parser is a Sphinx parser for the MyST markdown language.
When you use it, Sphinx will know how to parse content files that contain MyST markdown (by default, Sphinx will assume any files ending in `.md` are written in MyST markdown). Once a document has been parsed into Sphinx, it behaves the same way regardless of whether it has been written in rST or MyST markdown.

```
myst markdown (.md) ------> myst parser ---+
                                           |
                                           +-->Sphinx document (docutils)
                                           |
reStructuredText (.rst) --> rst parser ----+
```

For example, here's how you'd write a `toctree` directive in MyST markdown:

````
```{toctree}
My page name <page1>
page2
```
````

and here's the same in rST:

```
.. toctree::

   My page name <page1>
   page2
```

They will both behave the same in Sphinx.


[commonmark]: https://commonmark.org/
