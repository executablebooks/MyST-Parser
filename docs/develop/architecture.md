# The MyST implementation architecture

This page describes implementation details to help you understand the structure
of the project.

```{note}
MyST currently relies on
[a fork of the Mistletoe project](https://github.com/ExecutableBookProject/mistletoe).
We hope to upstream these changes, but in the meantime make sure that you are using
this fork.
```

## An extension to Mistletoe syntax

At a high level, the MyST parser is an extension of the Mistletoe project. Mistletoe
is a well-structured Python parser for CommonMark text. It also defines an extension
point to include more syntax in parsed files. The MyST parser uses this extension
point to define its own syntax options (e.g., for Sphinx roles and directives).

The result of this parser is a Mistletoe AST.

## A docutils renderer

The MyST parser also defines a docutils renderer for the Mistletoe AST. This allows us
to convert parsed elements of a MyST markdown file into docutils.

## A Sphinx parser

Finally, the MyST parser provides a parser for Sphinx, the documentation generation
system. This parser does the following:

* Parse markdown files with the MyST Mistletoe parser
* Convert these files into docutils objects using the MyST docutils renderer
* Provide these to Sphinx in order to use in building your site.
