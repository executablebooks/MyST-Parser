(example_syntax)=

# The MyST Syntax Guide

> {sub-ref}`today` | {sub-ref}`wordcount-minutes` min read

As a base, MyST adheres to the [CommonMark specification](https://spec.commonmark.org/).
For this, it uses the [markdown-it-py](https://github.com/executablebooks/markdown-it-py) parser,
which is a well-structured markdown parser for Python that is CommonMark-compliant
and also extensible.

MyST adds several new syntax options to CommonMark in order to be used
with Sphinx, the documentation generation engine used extensively in the Python
ecosystem.

Below is a summary of the syntax 'tokens' parsed,
and further details of a few major extensions from the CommonMark flavor of markdown.

:::{seealso}
- For an introduction to writing Directives and Roles with MyST markdown, see {ref}`intro/writing`.
- Check out the [MyST-Markdown VS Code extension](https://marketplace.visualstudio.com/items?itemName=ExecutableBookProject.myst-highlight), for MyST extended syntax highlighting.
:::

MyST builds on the tokens defined by markdown-it, to extend the syntax
described in the [CommonMark Spec](https://spec.commonmark.org/0.29/), which the parser is tested against.

% TODO link to markdown-it documentation

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
of lines just after the first line of the directive, each preceding with `:`. Then the
leading `:` is removed from each line, and the rest is parsed as YAML.

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

(syntax/directives/parsing)=
### How directives parse content

Some directives parse the content that is in their content block.
MyST parses this content **as Markdown**.

This means that MyST markdown can be written in the content areas of any directives written in MyST markdown. For example:

````md
```{admonition} My markdown link
Here is [markdown link syntax](https://jupyter.org)
```
````

```{admonition} My markdown link
Here is [markdown link syntax](https://jupyter.org)
```

As a short-hand for directives that require no arguments, and when no parameter options are used (see below),
you may start the content directly after the directive name.

````md
```{note} Notes require **no** arguments, so content can start here.
```
````

```{note} Notes require **no** arguments, so content can start here.
```

For special cases, MySt also offers the `eval-rst` directive.
This will parse the content **as ReStructuredText**:

````md
```{eval-rst}
.. figure:: img/fun-fish.png
  :width: 100px
  :name: rst-fun-fish

  Party time!

A reference from inside: :ref:`rst-fun-fish`

A reference from outside: :ref:`syntax/directives/parsing`
```
````

```{eval-rst}
.. figure:: img/fun-fish.png
  :width: 100px
  :name: rst-fun-fish

  Party time!

A reference from inside: :ref:`rst-fun-fish`

A reference from outside: :ref:`syntax/directives/parsing`
```

Note how the text is integrated into the rest of the document, so we can also reference [party fish](rst-fun-fish) anywhere else in the documentation.

### Nesting directives

You can nest directives by ensuring that the tick-lines corresponding to the
outermost directive are longer than the tick-lines for the inner directives.
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

### Markdown-friendly directives

Want to use syntax that renders correctly in standard Markdown editors?
See [the extended syntax option](syntax/colon_fence).

```md
:::{note}
This text is **standard** _Markdown_
:::
```

:::{note}
This text is **standard** _Markdown_
:::

(syntax/roles)=

## Roles - an in-line extension point

Roles are similar to directives - they allow you to define arbitrary new
functionality, but they are used *in-line*. To define an in-line
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

(syntax/roles/special)=

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

(syntax/frontmatter)=

## Front Matter

This is a YAML block at the start of the document, as used for example in
[jekyll](https://jekyllrb.com/docs/front-matter/).


:::{seealso}
Top-matter is also used for the [substitution syntax extension](syntax/substitutions),
and can be used to store information for blog posting (see [ablog's myst-parser support](https://ablog.readthedocs.io/manual/markdown/)).
:::

(syntax/html_meta)=

### Setting HTML Metadata

The front-matter can contain the special key `html_meta`; a dict with data to add to the generated HTML as [`<meta>` elements](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta).
This is equivalent to using the [RST `meta` directive](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#html-metadata).

HTML metadata can also be added globally in the `conf.py` *via* the `myst_html_meta` variable, in which case it will be added to all MyST documents.
For each document, the `myst_html_meta` dict will be updated by the document level front-matter `html_meta`, with the front-matter taking precedence.

:::{tabbed} Sphinx Configuration

```python
language = "en"
myst_html_meta = {
    "description lang=en": "metadata description",
    "description lang=fr": "description des métadonnées",
    "keywords": "Sphinx, MyST",
    "property=og:locale":  "en_US"
}
```

:::

:::{tabbed} MyST Front-Matter

```yaml
---
html_meta:
  "description lang=en": "metadata description"
  "description lang=fr": "description des métadonnées"
  "keywords": "Sphinx, MyST"
  "property=og:locale": "en_US"
---
```

:::

:::{tabbed} RestructuredText

```restructuredtext
.. meta::
   :description lang=en: metadata description
   :description lang=fr: description des métadonnées
   :keywords: Sphinx, MyST
   :property=og:locale: en_US
```

:::

:::{tabbed} HTML Output

```html
<html lang="en">
  <head>
    <meta content="metadata description" lang="en" name="description" xml:lang="en" />
    <meta content="description des métadonnées" lang="fr" name="description" xml:lang="fr" />
    <meta name="keywords" content="Sphinx, MyST">
    <meta content="en_US" property="og:locale" />
```

:::


(syntax/comments)=

## Comments

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

## Block Breaks

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

## Targets and Cross-Referencing

Targets are used to define custom anchors that you can refer to elsewhere in your
documentation. They generally go before section titles so that you can easily refer
to them.

:::{tip}

If you'd like to *automatically* generate targets for each of your section headers,
check out the [](syntax/header-anchors) section of extended syntaxes.

:::

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

is equivalent to using the [any inline role](https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-any):

```md
{any}`my text <header_target>`
```

but can also accept "nested" syntax (like bold text) and will recognise document paths that include extensions (e.g. `syntax/syntax` or `syntax/syntax.md`)

Using the same example, see this ref: [](syntax/targets), here is a reference back to the top of
this page: [my text with **nested** $\alpha$ syntax](example_syntax), and here is a reference to another page (`[](../sphinx/intro.md)`): [](../sphinx/intro.md).

```{note}
If you wish to have the target's title inserted into your text, you can
leave the "text" section of the markdown link empty. For example, this
markdown: `[](syntax.md)` will result in: [](syntax.md).
```

## Images

MyST provides a few different syntaxes for including images in your documentation.

The standard Markdown syntax is:

```md
![fishy](img/fun-fish.png)
```

![fishy](img/fun-fish.png)

But you can also enable extended image syntaxes, to control attributes like width and captions.
See the [extended image syntax guide](syntax/images).

(syntax/footnotes)=
## Footnotes

Footnotes use the [pandoc specification](https://pandoc.org/MANUAL.html#footnotes).
Their labels **start with `^`** and can then be any alpha-numeric string (no spaces), which is case-insensitive.

- If the label is an integer, then it will always use that integer for the rendered label (i.e. they are manually numbered).
- For any other labels, they will be auto-numbered in the order which they are referenced, skipping any manually numbered labels.

All footnote definitions are collected, and displayed at the bottom of the page (in the order they are referenced).
Note that un-referenced footnote definitions will not be displayed.

```md
- This is a manually-numbered footnote reference.[^3]
- This is an auto-numbered footnote reference.[^myref]

[^myref]: This is an auto-numbered footnote definition.
[^3]: This is a manually-numbered footnote definition.
```

- This is a manually-numbered footnote reference.[^3]
- This is an auto-numbered footnote reference.[^myref]

[^myref]: This is an auto-numbered footnote definition.
[^3]: This is a manually-numbered footnote definition.

Any preceding text after a footnote definitions, which is
indented by four or more spaces, will also be included in the footnote definition, and the text is rendered as MyST Markdown, e.g.

```md
A longer footnote definition.[^mylongdef]

[^mylongdef]: This is the _**footnote definition**_.

    That continues for all indented lines

    - even other block elements

    Plus any preceding unindented lines,
that are not separated by a blank line

This is not part of the footnote.
```

A longer footnote definition.[^mylongdef]

[^mylongdef]: This is the _**footnote definition**_.

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

This is because, in the current implementation, they may not be available to reference in text above that particular directive.
````

By default, a transition line (with a `footnotes` class) will be placed before any footnotes.
This can be turned off by adding `myst_footnote_transition = False` to the config file.


## Code blocks


### Show backticks inside raw markdown blocks

If you'd like to show backticks inside of your markdown, you can do so by nesting them
in backticks of a greater length. Markdown will treat the outer-most backticks as the
edges of the "raw" block and everything inside will show up. For example:

``` `` `hi` `` ```  will be rendered as: `` `hi` ``

and

`````
````
```
hi
```
````
`````

will be rendered as:

````
```
hi
```
````
