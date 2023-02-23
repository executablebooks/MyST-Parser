(syntax/core)=

# Typography

MyST is a strict superset of the [CommonMark syntax specification](https://spec.commonmark.org/).
It adds features focussed on scientific and technical documentation authoring, as detailed below.

## Headings

Markdown syntax denotes headers starting with between 1 to 6 #.

:::{myst-example}
### Heading Level 3
:::

Note, that headings that are not at the root level of the document
will not be included in the table of contents.
Using the [attrs_block](#syntax/attributes/block) extension,
you can also add classes to headings

:::{myst-example}
> {.bg-primary}
> ### Paragraph heading
:::

:::{seealso}
To structure single and multiple documents into table of contents, see the [organising content section](#organising-content).

To reference a heading in your text, see the [cross-referencing section](#syntax/referencing).
:::

## Paragraphs

Paragraphs are block of text separated by a blank line.

Using the [attrs_block](#syntax/attributes/block) extension,
you can also add classes to paragraphs:

:::{myst-example}
{.bg-primary}
Here is a paragraph with a class to control its formatting.
:::

(syntax/blockbreaks)=

## Thematic breaks

You can create a thematic break, to break content between themes, using three or more `*`, `-`, or `_` characters on a line by themselves.

:::{myst-example}
:alt-output: <hr class="docutils">
* * *
:::

## Inline Text Formatting

Standard inline formatting including bold, italic, code, as well as escaped symbols and line breaks:

:::{myst-example}
**strong**, _emphasis_, `literal text`, \*escaped symbols\*
:::

The [strikethrough](syntax/strikethrough) extension allows you to add strike-through text:

:::{myst-example}
~~strikethrough with *emphasis*~~
:::

The [smartquotes](syntax/smartquotes) and [replacements](syntax/replacements) extensions can improve the typography of common symbols:


:::{myst-example}
Smart-quotes 'single quotes' and "double quotes".

+-, --, ---, ... and other replacements.
:::

Using the [attrs_inline](syntax/attributes/inline) extension,
you can also add classes to inline text spans:

:::{myst-example}
A paragraph with a span of [text with attributes]{.bg-warning}
:::

## Line Breaks

To put a line break, without a paragraph, use a `\` followed by a new line. This corresponds to a `<br>` in HTML and `\\` in LaTeX.

:::{myst-example}
Fleas \
Adam \
Had 'em.
:::

## Bullet points and numbered lists

You can use bullet points and numbered lists as you would in standard Markdown.
Starting a line with either a `-` or `*` for a bullet point, and `1.` for numbered lists.
These lists can be nested using two spaces at the start of the line.

:::{myst-example}
- Lists can start with `-` or `*`
  * My other, nested
  * bullet point list!

1. My numbered list
2. has two points
:::

For numbered lists, you can start following lines with any number, meaning they don't have to be in numerical order, and this will not change the rendered output.
The exception is the first number, which if it is not `1.` this will change the start number of the list.

::::{admonition} Alternate numbering styles
:class: tip dropdown

Using the [attrs_block](#syntax/attributes/block) extension,
you can also specify a alternative numbering styles:

:::{myst-example}
{style=lower-alpha}
1. a
2. b

{style=upper-alpha}
1. a
2. b

{style=lower-roman}
1. a
2. b

{style=upper-roman}
1. a
2. b
:::

::::

Using the [tasklist](syntax/tasklists) extension,
you can also create task lists:

:::{myst-example}
- [ ] An item that needs doing
- [x] An item that is complete
:::

## Subscript & Superscript

For inline typography for subscript and superscript formatting,
the `sub` and `sup` {{role}}, can be used respectively.

:::{myst-example}
H{sub}`2`O, and 4{sup}`th` of July
:::


## Quotations

Quotations are controlled with standard Markdown syntax, by inserting a caret (>) symbol in front of one or more lines of text.

:::{myst-example}
> We know what we are, but know not what we may be.
:::

Using the [attrs_block](#syntax/attributes/block) extension,
you can also add an `attribution` attribute to a block quote:

:::{myst-example}
{attribution="Hamlet act 4, Scene 5"}
> We know what we are, but know not what we may be.
:::

(syntax/glossaries)=
## Definition lists and glossaries

Using the [definition lists](syntax/definition-lists) extension,
you can define terms in your documentation, using the syntax:

:::{myst-example}
Term 1
: Definition

Term 2
: Longer definition

  With multiple paragraphs

  - And bullet points

:::

Using the [attrs_block](#syntax/attributes/block) extension,
you can also add a `glossary` class to a definition list, that will allow you to reference terms in your text using the [`term` role](syntax/roles):

:::{myst-example}
{.glossary}
my term
: Definition of the term

{term}`my term`
:::

## Field lists

Using the [field lists](syntax/fieldlists) extension,
you can create field lists, which are useful in source code documentation (see [Sphinx docstrings](inv:sphinx#info-field-lists)):

:::{myst-example}

:param arg1: A description of arg1
:param arg2: A longer description,
    with multiple lines.

    - And bullet points
:return: A description of the return value

:::

(syntax/comments)=

## Comments

You may add comments by putting the `%` character at the beginning of a line. This will
prevent the line from being parsed into the output document.

For example, this won't be parsed into the document:

:::{myst-example}
% my comment
:::

::::{admonition} Comments split paragraphs
:class: warning dropdown

Since comments are a block-level entity, they will terminate the previous block.
In practical terms, this means that the following lines
will be broken up into two paragraphs, resulting in a new line between them:

:::{myst-example}
a line
% a comment
another line
:::

::::

(syntax/footnotes)=
## Footnotes

Footnotes use the [pandoc specification](https://pandoc.org/MANUAL.html#footnotes).
Their labels **start with `^`** and can then be any alphanumeric string (no spaces), which is case-insensitive.

- If the label is an integer, then it will always use that integer for the rendered label (i.e. they are manually numbered).
- For any other labels, they will be auto-numbered in the order which they are referenced, skipping any manually numbered labels.

All footnote definitions are collected, and displayed at the bottom of the page (in the order they are referenced).
Note that un-referenced footnote definitions will not be displayed.

:::{myst-example}
- This is a manually-numbered footnote reference.[^3]
- This is an auto-numbered footnote reference.[^myref]

[^myref]: This is an auto-numbered footnote definition.
[^3]: This is a manually-numbered footnote definition.
:::

Any preceding text after a footnote definitions, which is
indented by four or more spaces, will also be included in the footnote definition, and the text is rendered as MyST Markdown, e.g.

:::{myst-example}
A longer footnote definition.[^mylongdef]

[^mylongdef]: This is the _**footnote definition**_.

    That continues for all indented lines

    - even other block elements

    Plus any preceding unindented lines,
that are not separated by a blank line

This is not part of the footnote.
:::

````{important}
Although footnote references can be used just fine within directives, e.g.[^myref],
it is recommended that footnote definitions are not set within directives,
unless they will only be referenced within that same directive:

This is because, they may not be available to reference in text outside that particular directive.
````

By default, a transition line (with a `footnotes` class) will be placed before any footnotes.
This can be turned off by adding `myst_footnote_transition = False` to the config file.
