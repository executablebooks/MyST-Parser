# Frequently Asked Questions

This page covers some frequently-asked questions about the MyST markdown language,
as well as the MyST parser for Sphinx. If you're just getting started, see {doc}`intro`.

## What is the relationship between MyST, reStructuredText, and Sphinx?

MyST markdown provides a markdown equivalent of the reStructuredText syntax,
meaning that you can do anything in MyST that you can do with reStructuredText.

Sphinx has its own internal document model, and by default it knows how to convert
reStructuredText into that document model (with an rST parser). The MyST markdown language
defines markdown syntax that has all of the functionality that Sphinx provides (most
notable, directives, roles, and labels). The MyST parser is a Sphinx extension that can
parse this flavor of markdown into Sphinx's internal document model. Once a document
has been parsed into Sphinx, it behaves the same way regardless of whether it has
been written in rST or MyST markdown.

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

## What markup language should I use inside directives?

If you need to parse content *inside* of another block of content (for example, the
content inside a **note directive**), note that the MyST parser will be used for this
nested parsing as well.

## Why doesn't my role/directive recognize markdown link syntax?

There are some roles/directives that _hard-code_ syntax into
their behavior. For example, many roles allow you to supply titles for links like so:
`` {role}`My title <myref>` ``. While this looks like reStructuredText, the role may
be explicitly expecting the `My title <myref>` structure, and so MyST will behave the same way.

## How fast is the `myst-parser`?

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

The MyST parser is slightly slower than the base `markdown-it-py` parser,
due to the additional syntax which it parses and the conversion to docutils AST,
but even then it is still comparably performant to the other parsers parser.

:::{seealso}
The [markdown-it-py performance documentation](markdown_it:md/performance).
:::
