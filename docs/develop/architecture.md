# The MyST implementation architecture

This page describes implementation details to help you understand the structure
of the project.

## A Renderer for markdown-it tokens

At a high level, the MyST parser is an extension of the Markdown-It-Py project. Markdown-It-Py
is a well-structured Python parser for CommonMark text. It also defines an extension
point to include more syntax in parsed files. The MyST parser uses this extension
point to define its own syntax options (e.g., for Sphinx roles and directives).

The result of this parser is a markdown-it token stream.

## A docutils renderer

The MyST parser also defines a docutils renderer for the markdown-it token stream.
This allows us to convert parsed elements of a MyST markdown file into docutils.

## A Sphinx parser

Finally, the MyST parser provides a parser for Sphinx, the documentation generation
system. This parser does the following:

* Parse markdown files with the markdown-it parser, including MyST specific plugins
* Convert these files into docutils objects using the MyST docutils renderer
* Provide these to Sphinx in order to use in building your site.

## Extracting directive text

Tools that inspect directive source without rendering it can use
`myst_parser.parsers.directives.parse_directive_text(None, "", content)`.
Passing `None` instead of a docutils directive class extracts arbitrary option
names as strings, including empty flags, without applying a directive's option
converters. Both colon-prefixed options and YAML-style option blocks are supported.
Syntax errors still produce warnings with source locations.

The result includes `options`, normalized `body` lines and `body_offset`.
For tools that need exact source whitespace, use `body_offset` to locate the
body in the original content rather than joining the normalized lines.
The empty second argument means there is no body text on the directive's opening
line. If supplied, that text is included in the body, as with a directive that
takes no arguments.
