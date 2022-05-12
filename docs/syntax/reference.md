(syntax-tokens)=
# Syntax tokens

This page serves as a reference for the syntax that makes of MyST Markdown.

:::{seealso}
For more description and explanation of MyST syntax, see the [syntax guide](syntax.md).
:::

## Block (Multi-line) Tokens

Block tokens span multiple lines of content. They are broken down into two sections:

- {ref}`extended-block-tokens` contains *extra* tokens that are not in CommonMark.
- {ref}`commonmark-block-tokens` contains CommonMark tokens that also work, for reference.

:::{note}
Because MyST markdown was inspired by functionality that exists in reStructuredText,
we have shown equivalent rST syntax for many MyST markdown features below.
:::

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
  - `$$` (default) or `\[`...`\]` characters wrapping multi-line math, or even direct [amsmath](https://ctan.org/pkg/amsmath) LaTeX equations (optional).
  See {ref}`syntax/math` for more information.
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
* - Admonitions (optional)
  - An alternative approach for admonition style directives only, which has the benefit of allowing the content to be rendered in standard markdown editors.
    See [admonition directives](syntax/admonitions) for more details.
  - ````md
    :::{note}
    *content*
    :::
    ````
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
  - Quoted text
  - ```md
    > this is a quote
    ```
* - CodeFence
  - Enclosed in 3 or more `` ` `` or `~` with an optional language name.
    See {ref}`syntax/code-blocks` for more information.
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

## Span (Inline) Tokens

Span (or inline) tokens are defined on a single line of content. They are broken down into two
sections below:

- {ref}`extended-span-tokens` contains *extra* tokens that are not in CommonMark.
- {ref}`commonmark-span-tokens` contains CommonMark tokens that also work, for reference.

(extended-span-tokens)=
### Extended inline tokens

`````{list-table}
:header-rows: 1
:widths: 10 20 20

* - Token
  - Description
  - Example
* - Role
  - See {ref}`syntax/roles` for more information.
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
  - `$` (default) or `\(`...`\)` enclosed math. See
  {ref}`syntax/math` for more information.
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
  - Any valid HTML (rendered in HTML output only)
  - ```html
    <p>some text</p>
    ```
* - EscapeSequence
  - Escaped symbols (to avoid them being interpreted as other syntax elements)
  - ```md
    \*
    ```
* - AutoLink
  - Link that is shown in final output
  - ```md
    <http://www.google.com>
    ```
* - InlineCode
  - Literal text
  - ```md
    `a=1`
    ```
* - LineBreak
  - Soft or hard (ends with spaces or backslash)
  - ```md
    A hard break\
    ```
* - Image
  - Link to an image.
    You can also use HTML syntax, to include image size etc, [see here](syntax/images) for details
  - ```md
    ![alt](src "title")
    ```
* - Link
  - Reference `LinkDefinitions`. See {ref}`syntax/referencing` for more details.
  - ```md
    [text](target "title") or [text][key]
    ```
* - Strong
  - Bold text
  - ```md
    **strong**
    ```
* - Emphasis
  - Italic text
  - ```md
    *emphasis*
    ```
* - RawText
  - Any text
  - ```md
    any text
    ```
`````
