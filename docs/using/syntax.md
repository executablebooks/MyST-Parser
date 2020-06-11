(example_syntax)=

# The MyST Syntax Guide

As a base, MyST adheres to the [CommonMark specification](https://spec.commonmark.org/).
For this, it uses the [markdown-it-py](https://github.com/executablebooks/markdown-it-py) parser,
which is a well-structured markdown parser for Python that is CommonMark-compliant
and also extensible.

MyST adds several new syntax options to CommonMark in order to be used
with Sphinx, the documentation generation engine used extensively in the Python
ecosystem.

Below is a summary of the syntax 'tokens' parsed,
and further details of a few major extensions from the CommonMark flavor of markdown.

```{seealso}
For an introduction to writing Directives and Roles with MyST markdown, see {ref}`intro/writing`.
```

% ```{seealso}
% {ref}`MyST Extended AST Tokens API <api/tokens>`
% ```

MyST builds on the tokens defined by markdown-it, to extend the syntax
described in the [CommonMark Spec](https://spec.commonmark.org/0.29/), which the parser is tested against.

% TODO link to markdown-it documentation

## Block Tokens Summary

Block tokens span multiple lines of content. They are broken down into two sections:

* {ref}`extended-block-tokens` contains *extra* tokens that are not in CommonMark.
* {ref}`commonmark-block-tokens` contains CommonMark tokens that also work, for reference.

In addition to these summaries of block-level syntax, see {ref}`extra-markdown-syntax`.

```{note}
Because MyST markdown was inspired by functionality that exists in reStructuredText,
we have shown equivalent rST syntax for many MyST markdown features below.
```

(extended-block-tokens)=
### Extended block tokens

`````{list-table}
:header-rows: 1
:widths: 10 20 20

* - Token
  - Description
  - Example
* - FrontMatter
  - A YAML block at the start of the document enclosed by `---`
  - ```yaml
    ---
    key: value
    ---
    ```
* - Directives
  - enclosed in 3 or more backticks followed by the directive name wrapped
  in curly brackets `{}`. See {ref}`syntax/directives` for more details.
  - ````md
    ```{directive}
    :option: value

    content
    ```
    ````
* - Math
  - Two `$` characters wrapping multi-line math
  - ```latex
    $$
    a=1
    $$
    ```
* - Table
  - Standard markdown table style, with pipe separation.
  - ```md
    | a    | b    |
    | :--- | ---: |
    | c    | d    |
    ```
* - LineComment
  - A commented line. See {ref}`syntax/comments` for more information.
  - ```latex
    % this is a comment
    ```
* - BlockBreak
  - Define blocks of text. See {ref}`syntax/blockbreaks` for more information.
  - ```md
    +++ {"meta": "data"}
    ```
* - Footnote
  - A definition for a referencing footnote, that is placed at the bottom of the document.
   See {ref}`syntax/footnotes` for more details.
  - ```md
    [^ref]: Some footnote text
    ```
`````

(commonmark-block-tokens)=
### CommonMark tokens

`````{list-table}
:header-rows: 1
:widths: 10 20 20

* - Token
  - Description
  - Example
* - HTMLBlock
  - Any valid HTML (rendered in HTML output only)
  - ```html
    <p>some text</p>
    ```
* - BlockCode
  - indented text (4 spaces or a tab)
  - ```md
        included as literal *text*
    ```
* - Heading
  - Level 1-6 headings, denoted by number of `#`
  - ```md
    ### Heading level 3
    ```
* - SetextHeading
  - Underlined header (using multiple `=` or `-`)
  - ```md
    Header
    ======
    ```
* - Quote
  - quoted text
  - ```md
    > this is a quote
    ```
* - CodeFence
  - enclosed in 3 or more backticks with an optional language name
  - ````md
    ```python
    print('this is python')
    ```
    ````
* - ThematicBreak
  - Creates a horizontal line in the output
  - ```md
    ---
    ```
* - List
  - bullet points or enumerated.
  - ```md
    - item
      - nested item
    1. numbered item
    ```
* - LinkDefinition
  -  A substitution for an inline link, which can have a reference target (no spaces), and an optional title (in `"`)
  - ```md
    [key]: https://www.google.com "a title"
    ```
* - Paragraph
  - General inline text
  - ```md
    any *text*
    ```
`````

## Span (Inline) Tokens Summary

Span (or inline) tokens are defined on a single line of content. They are broken down into two
sections below:

* {ref}`extended-span-tokens` contains *extra* tokens that are not in CommonMark.
* {ref}`commonmark-span-tokens` contains CommonMark tokens that also work, for reference.

In addition to these summaries of inline syntax, see {ref}`extra-markdown-syntax`.

(extended-span-tokens)=
### Extended inline tokens

`````{list-table}
:header-rows: 1
:widths: 10 20 20

* - Token
  - Description
  - Example
* - Role
  - See {ref}`syntax/roles` for more
  information.
  - ```md
    {rolename}`interpreted text`
    ```
* - Target
  - Precedes element to target, e.g. header. See
  {ref}`syntax/targets` for more information.
  - ```md
    (target)=
    ```
* - Math
  - dollar enclosed math
  - ```latex
    $a=1$ or $$a=1$$
    ```
* - FootReference
  - Reference a footnote. See {ref}`syntax/footnotes` for more details.
  - ```md
    [^abc]
    ```
`````

(commonmark-span-tokens)=
### CommonMark inline tokens

`````{list-table}
:header-rows: 1
:widths: 10 20 20

* - Token
  - Description
  - Example
* - HTMLSpan
  - any valid HTML (rendered in HTML output only)
  - ```html
    <p>some text</p>
    ```
* - EscapeSequence
  - escaped symbols (to avoid them being interpreted as other syntax elements)
  - ```md
    \*
    ```
* - AutoLink
  - link that is shown in final output
  - ```md
    <http://www.google.com>
    ```
* - InlineCode
  - literal text
  - ```md
    `a=1`
    ```
* - LineBreak
  - Soft or hard (ends with spaces or backslash)
  - ```md
    A hard break\
    ```
* - Image
  - link to an image
  - ```md
    ![alt](src "title")
    ```
* - Link
  - Reference `LinkDefinitions`
  - ```md
    [text](target "title") or [text][key]
    ```
* - Strong
  - bold text
  - ```md
    **strong**
    ```
* - Emphasis
  - italic text
  - ```md
    *emphasis*
    ```
* - RawText
  - any text
  - ```md
    any text
    ```
`````

(syntax/directives)=

## Directives - a block-level extension point

Directives syntax is defined with triple-backticks and curly-brackets. It
is effectively a code block with curly brackets around the language, and
a directive name in place of a language name. It is similar to how RMarkdown
defines "runnable cells". Here is the basic structure:

`````{list-table}
---
header-rows: 1
---
* - MyST
  - reStructuredText
* - ````md
    ```{directivename} arguments
    ---
    key1: val1
    key2: val2
    ---
    This is
    directive content
    ```
    ````
  - ```rst
    .. directivename:: arguments
       :key1: val1
       :key2: val2

       This is
       directive content
    ```
`````

For example, the following code:

````md
```{admonition} This is my admonition
This is my note
```
````

Will generate this admonition:

```{admonition} This is my admonition
This is my note
```

### Parameterizing directives

For directives that take parameters as input, there are two ways to parameterize them.
In each case, the options themselves are given as `key: value` pairs. An example of
each is shown below:

**Using YAML frontmatter**. A block of YAML front-matter just after the
first line of the directive will be parsed as options for the directive. This needs to be
surrounded by `---` lines. Everything in between will be parsed by YAML and
passed as keyword arguments to your directive. For example:

````md
```{code-block} python
---
lineno-start: 10
emphasize-lines: 1, 3
caption: |
    This is my
    multi-line caption. It is *pretty nifty* ;-)
---
a = 2
print('my 1st line')
print(f'my {a}nd line')
```
````

```{code-block} python
---
lineno-start: 10
emphasize-lines: 1, 3
caption: |
    This is my
    multi-line caption. It is *pretty nifty* ;-)
---
a = 2
print('my 1st line')
print(f'my {a}nd line')
```

**Short-hand options with `:` characters**. If you only need one or two options for your
directive and wish to save lines, you may also specify directive options as a collection
of lines just after the first line of the directive, each preceding with `:`.

For example:

````md
```{code-block} python
:lineno-start: 10
:emphasize-lines: 1, 3

a = 2
print('my 1st line')
print(f'my {a}nd line')
```
````

### How directives parse content

Some directives parse the content that is in their content block. This
means that MyST markdown can be written in the content areas of any directives written
in MyST markdown. For example:

````md
```{admonition} My markdown link
Here is [markdown link syntax](https://jupyter.org)
```
````

```{admonition} My markdown link
Here is [markdown link syntax](https://jupyter.org)
```

As a short-hand for directives that require no arguments, and when no paramter options are used (see below),
you may start the content directly after the directive name.

````md
```{note} Notes require **no** arguments, so content can start here.
```
````

```{note} Notes require **no** arguments, so content can start here.
```

### Nesting directives

You can nest directives by ensuring that the ticklines corresponding to the
outermost directive are longer than the ticklines for the inner directives.
For example, nest a warning inside a note block like so:

`````md
````{note}
The next info should be nested
```{warning}
Here's my warning
```
````
`````

Here's how it looks rendered:

````{note}
The next info should be nested
```{warning}
Here's my warning
```
````

You can indent inner-code fences, so long as they aren't indented by more than 3 spaces.
Otherwise, they will be rendered as "raw code" blocks:

`````md
````{note}
The warning block will be properly-parsed

   ```{warning}
   Here's my warning
   ```

But the next block will be parsed as raw text

    ```{warning}
    Here's my raw text warning that isn't parsed...
    ```
````
`````

````{note}
The warning block will be properly-parsed

   ```{warning}
   Here's my warning
   ```

But the next block will be parsed as raw text

    ```{warning}
    Here's my raw text warning that isn't parsed...
    ```
````

This can really be abused if you'd like ;-)

``````{note}
The next info should be nested
`````{warning}
Here's my warning
````{admonition} Yep another admonition
```python
# All this fuss was about this boring python?!
print('yep!')
```
````
`````
``````

(syntax/roles)=

## Roles - an in-line extension point

Roles are similar to directives - they allow you to define arbitrary new
functionality in Sphinx, but they are used *in-line*. To define an in-line
role, use the following form:

````{list-table}
---
header-rows: 1
---
* - MyST
  - reStructuredText
* - ````md
    {role-name}`role content`
    ````
  - ```rst
    :role-name:`role content`
    ```
````

For example, the following code:

```md
Since Pythagoras, we know that {math}`a^2 + b^2 = c^2`
```

Becomes:

Since Pythagoras, we know that {math}`a^2 + b^2 = c^2`

You can use roles to do things like reference equations and other items in
your book. For example:

````md
```{math} e^{i\pi} + 1 = 0
---
label: euler
---
```

Euler's identity, equation {math:numref}`euler`, was elected one of the
most beautiful mathematical formulas.
````

Becomes:

```{math} e^{i\pi} + 1 = 0
---
label: euler
---
```

Euler's identity, equation {math:numref}`euler`, was elected one of the
most beautiful mathematical formulas.

### How roles parse content

The content of roles is parsed differently depending on the role that you've used.
Some roles expect inputs that will be used to change functionality. For example,
the `ref` role will assume that input content is a reference to some other part of the
site. However, other roles may use the MyST parser to parse the input as content.

Some roles also **extend their functionality** depending on the content that you pass.
For example, following the `ref` example above, if you pass a string like this:
`Content to display <myref>`, then the `ref` will display `Content to display` and use
`myref` as the reference to look up.

How roles parse this content depends on the author that created the role.

(extra-markdown-syntax)=
## Extra markdown syntax

In addition to roles and directives, MyST supports extra markdown syntax that doesn't
exist in CommonMark. In most cases, these are syntactic short-cuts to calling
roles and directives. We'll cover some common ones below.

This table describes the rST and MyST equivalents:

````{list-table}
---
header-rows: 1
---
* - Type
  - MyST
  - reStructuredText
* - Math shortcuts
  - `$x^2$`
  - N/A
* - Front matter
  - ```md
    ---
    key: val
    ---
    ```
  - ```md
    :key: val
    ```
* - Comments
  - `% comment`
  - `.. comment`
* - Targets
  - `(mytarget)=`
  - `.. _mytarget:`
````

### Math shortcuts

Math can be called in-line with single `$` characters around your math.
For example, `$x_{hey}=it+is^{math}$` renders as $x_{hey}=it+is^{math}$.
This is equivalent to writing:

```md
{math}`x_{hey}=it+is^{math}`
```

Block-level math can be provided with `$$` signs that wrap the math block you'd like
to parse. For example:

```latex
$$
   \begin{eqnarray}
      y    & = & ax^2 + bx + c \\
      f(x) & = & x^2 + 2xy + y^2
   \end{eqnarray}
$$
```

becomes

$$
   \begin{eqnarray}
      y    & = & ax^2 + bx + c \\
      f(x) & = & x^2 + 2xy + y^2
   \end{eqnarray}
$$

This is equivalent to the following directive:

````md
```{math}
   \begin{eqnarray}
      y    & = & ax^2 + bx + c \\
      f(x) & = & x^2 + 2xy + y^2
   \end{eqnarray}
```
````

You can also add labels to block equations:

```latex
$$
e = mc^2
$$ (eqn:best)

This is the best equation {eq}`eqn:best`
```

$$
e = mc^2
$$ (eqn:best)

This is the best equation {eq}`eqn:best`

(syntax/frontmatter)=

### Front Matter

This is a YAML block at the start of the document, as used for example in
[jekyll](https://jekyllrb.com/docs/front-matter/). Sphinx intercepts these data and
stores them within the global environment (as discussed
[here](https://www.sphinx-doc.org/en/master/usage/restructuredtext/field-lists.html)).

A classic use-case is to specify 'orphan' documents, that are not specified in any
toctrees. For example, inserting the following syntax at the top of a page will cause
Sphinx to treat it as an orphan page:

```md
---
orphan: true
---

This is an orphan document, not specified in any toctrees.
```

(syntax/comments)=

### Comments

You may add comments by putting the `%` character at the beginning of a line. This will
prevent the line from being parsed into the output document.

For example, this code:

```md
% my comment
```

Is below, but it won't be parsed into the document.

% my comment

````{important}
Since comments are a block-level entity, they will terminate the previous block.
In practical terms, this means that the following lines
will be broken up into two paragraphs, resulting in a new line between them:

```
a line
% a comment
another line
```

a line
% a comment
another line
````

(syntax/blockbreaks)=

### Block Breaks

You may add a block break by putting `+++` at the beginning of a line.
This constuct's intended use case is for mapping to cell based document formats,
like [jupyter notebooks](https://jupyter.org/),
to indicate a new text cell. It will not show up in the rendered text,
but is stored in the internal document structure for use by developers.

For example, this code:

```md
+++ some text
```

Is below, but it won't be parsed into the document.

+++

(syntax/targets)=

### Targets and Cross-Referencing

Targets are used to define custom anchors that you can refer to elsewhere in your
documentation. They generally go before section titles so that you can easily refer
to them.

```{tip}
If you'd like to *automatically* generate targets for each of your section headers,
check out the [`autosectionlabel`](https://www.sphinx-doc.org/en/master/usage/extensions/autosectionlabel.html)
sphinx feature. See {ref}`autosectionlabel` for more details.
```

Target headers are defined with this syntax:

```md
(header_target)=
```

They can then be referred to with the [ref inline role](https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-ref):

```md
{ref}`header_target`
```

By default, the reference will use the text of the target (such as the section title), but also you can directly specify the text:

```md
{ref}`my text <header_target>`
```

For example, see this ref: {ref}`syntax/targets`, and here's a ref back to the top of
this page: {ref}`my text <example_syntax>`.

Alternatively using the markdown syntax:

```md
[my text](header_target)
```

is synonymous with using the [any inline role](https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-any):

```md
{any}`my text <header_target>`
```

Using the same example, see this ref: [](syntax/targets), and here's a ref back to the top of
this page: [my text](example_syntax).

(syntax/footnotes)=

### Footnotes

Footnote labels **start with `^`** and can then be any alpha-numeric string (no spaces),
which is case-insensitive.
The actual label is not displayed in the rendered text; instead they are numbered,
in the order which they are referenced.
All footnote definitions are collected, and displayed at the bottom of the page
(ordered by number).
Note that un-referenced footnote definitions will not be displayed.

```md
This is a footnote reference.[^myref]

[^myref]: This **is** the footnote definition.
```

This is a footnote reference.[^myref]

[^myref]: This **is** the footnote definition.

Any preceding text after a footnote definitions, which is
indented by four or more spaces, will also be included in the footnote definition, e.g.

```md
A longer footnote definition.[^mylongdef]

[^mylongdef]: This is the footnote definition.

    That continues for all indented lines

    - even other block elements

    Plus any preceding unindented lines,
that are not separated by a blank line

This is not part of the footnote.
```

A longer footnote definition.[^mylongdef]

[^mylongdef]: This is the footnote definition.

    That continues for all indented lines

    - even other block elements

    Plus any preceding unindented lines,
that are not separated by a blank line

This is not part of the footnote.

````{important}
Although footnote references can be used just fine within directives, e.g.[^myref],
it it recommended that footnote definitions are not set within directives,
unless they will only be referenced within that same directive:

```md
[^other]

[^other]: A definition within a directive
```

[^other]

[^other]: A definition within a directive

This is because, in the current implementation, they may not be available to
reference in text above that particular directive.
````
