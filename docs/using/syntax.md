(example_syntax)=

# Example syntax for MyST

As a base, MyST adheres to the [CommonMark specification](https://spec.commonmark.org/).
For this, it uses the [Mistletoe project](https://github.com/miyuchina/mistletoe),
which is a well-structured markdown parser for Python that is CommonMark-compliant
and also extensible.

MyST adds several new syntax options that extend its functionality to be used
with Sphinx, the documentation generation engine used extensively in the Python
ecosystem. Sphinx uses reStructuredText by default, which is both more
powerful than Markdown, and also (arguably) more complex to use.

This project is an attempt to have the best of both worlds: the flexibility
and extensibility of Sphinx with the simplicity and readability of Markdown.

Below is a summary of the syntax 'tokens' parsed,
and further details of a few major extensions from the CommonMark flavor of markdown

## Parsed Token Classes

Tokens are listed in their order of precedence.
For more information, also see the [CommonMark Spec](https://spec.commonmark.org/0.28/), which the parser is tested against.

### Block Tokens

#### Extended block tokens

- **FrontMatter**: A YAML block at the start of the document enclosed by `---`. See
  {ref}`syntax/frontmatter` for more information.
- **Directives**: enclosed in 3 or more backticks followed by the directive name wrapped
  in curly brackets `{}`. See {ref}`syntax/directives` for more details.
- **Math**: Two `$` characters wrapping multi-line math, e.g.

  ```
  $$
  a=1
  $$
  ```
- **LineComment**: `% this is a comment`. See {ref}`syntax/comments` for more
  information.
- **BlockBreak**: `+++`. See {ref}`syntax/blockbreaks` for more information.

#### CommonMark tokens

- **HTMLBlock**: Any valid HTML (rendered in HTML output only)
- **BlockCode**: indented text (4 spaces)
- **Heading**: `# Heading` (levels 1-6)
- **SetextHeading**: underlined header (using multiple `=` or `-`)
- **Quote**: `> this is a quote`
- **CodeFence**: enclosed in 3 or more backticks with an optional language name. E.g.:
  ````
  ```python
  print('this is python')
  ```
  ````
- **ThematicBreak**: `---`
- **List**: bullet points or enumerated.
- **Table**: Standard markdown table styles.
- **Footnote**: A substitution for an inline link (e.g. `[key][name]`), which can have a reference target (no spaces), and an optional title (in `"`), e.g. `[key]: https://www.google.com "a title"`
- **Paragraph**: General inline text

### Span (Inline) Tokens

#### Extended inline tokens

- **Role**: `` `{rolename}`interpreted text` ``. See {ref}`syntax/roles` for more
  information.
- **Target**: `(target)=` (precedes element to target, e.g. header). See
  {ref}`syntax/targets` for more information.
- **Math**: `$a=1$` or `$$a=1$$`

#### CommonMark inline tokens

- **HTMLSpan**: any valid HTML (rendered in HTML output only)
- **EscapeSequence**: `\*`
- **AutoLink**: `<http://www.google.com>`
- **InlineCode**: `` `a=1` ``
- **LineBreak**: Soft or hard (ends with spaces or `\`)
- **Image**: `![alt](src "title")`
- **Link**: `[text](target "title")` or `[text][key]` (key from `Footnote`)
- **Strong**: `**strong**`
- **Emphasis**: `*emphasis*`
- **RawText**

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
* - ````markdown
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

````
```{admonition} This is my admonition
This is my note
```
````

Will generate this admonition:

```{admonition} This is my admonition
This is my note
```

For directives that are meant to parse content for your site, you may use
markdown as the markup language inside...

````
```{admonition} My markdown link
Here is [markdown link syntax](https://jupyter.org)
```
````

```{admonition} My markdown link
Here is [markdown link syntax](https://jupyter.org)
```

### Parameterizing directives

For directives that take parameters as input, you may parameterize them by
beginning your directive content with YAML frontmatter. This needs to be
surrounded by `---` lines. Everything in between will be parsed by YAML and
passed as keyword arguments to your directive. For example:

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

As a short-hand alternative, more closely resembling the reStructuredText syntax, options may also be denoted by an initial block, whereby all lines start with '`:`', for example:

````
```{code-block} python
:lineno-start: 10
:emphasize-lines: 1, 3

a = 2
print('my 1st line')
print(f'my {a}nd line')
```
````

### Nesting directives

You can nest directives by ensuring that the ticklines corresponding to the
outermost directive are longer than the ticklines for the inner directives.
For example, nest a warning inside a note block like so:

`````
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
functionality in Sphinx, but they are use *in-line*. To define an in-line
role, use the following form:

````{list-table}
---
header-rows: 1
---
* - MyST
  - reStructuredText
* - ````markdown
    {role-name}`role content`
    ````
  - ```rst
    :role-name:`role content`
    ```
````

For example, the following code:

```
Since Pythagoras, we know that {math}`a^2 + b^2 = c^2`
```

Becomes:

Since Pythagoras, we know that {math}`a^2 + b^2 = c^2`

You can use roles to do things like reference equations and other items in
your book. For example:

````
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

## Extra markdown syntax

Here is some extra markdown syntax which provides functionality in rST that doesn't
exist in CommonMark. In most cases, these are syntactic short-cuts to calling
roles and directives. We'll cover some common ones below.

This tale describes the rST and MyST equivalents:

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
  - ```
    ---
    key: val
    ---
    ```
  - ```
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

```
{math}`x_{hey}=it+is^{math}`
```

Block-level math can be provided with `$$` signs that wrap the math block you'd like
to parse. For example:

```
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

````
```{math}
   \begin{eqnarray}
      y    & = & ax^2 + bx + c \\
      f(x) & = & x^2 + 2xy + y^2
   \end{eqnarray}
```
````

(syntax/frontmatter)=
### Front Matter

This is a YAML block at the start of the document, as used for example in
[jekyll](https://jekyllrb.com/docs/front-matter/). Sphinx intercepts this data and
stores it within the global environment (as discussed
[here](https://www.sphinx-doc.org/en/master/usage/restructuredtext/field-lists.html)).

A classic use-case is to specify 'orphan' documents, that are not specified in any
toctrees. For example, inserting the following syntax at the top of a page will cause
Sphinx to treat it as an orphan page:

```markdown
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

```
% my comment
```

Is below, but it won't be parsed into the document.

% my comment

(syntax/blockbreaks)=

### Block Breaks

You may add a block break by putting `+++` at the beginning of a line.
This constuct's intended use case is for mapping to cell based document formats,
like [jupyter notebooks](https://jupyter.org/),
to indicate a new text cell. It will not show up in the rendered text,
but is stored in the internal document structure for use by developers.

For example, this code:

```
+++ some text
```

Is below, but it won't be parsed into the document.

+++

(syntax/targets)=

### Targets and Cross-Referencing

Targets are used to define custom anchors that you can refer to elsewhere in your
documentation. They generally go before section titles so that you can easily refer
to them.

Target headers are defined with this syntax:

```
(header_target)=
```

They can then be referred to with the [ref inline role](https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-ref):

```
{ref}`header_target`
```

By default, the reference will use the text of the target (such as the section title), but also you can directly specify the text:

```
{ref}`my text <header_target>`
```

For example, see this ref: {ref}`syntax/targets`, and here's a ref back to the top of
this page: {ref}`my text <example_syntax>`.

Alternatively using the markdown syntax:

```markdown
[my text](header_target)
```

is synonymous with using the [any inline role](https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-any):

```
{any}`my text <header_target>`
```

Using the same example, see this ref: [](syntax/targets), and here's a ref back to the top of
this page: [my text](example_syntax).
