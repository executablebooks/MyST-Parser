(syntax/core)=

# Core Syntax

## Introduction

MyST is a strict superset of the [CommonMark syntax specification](https://spec.commonmark.org/).
It adds features focussed on scientific and technical documentation authoring, as detailed below.

In addition, the roles and directives syntax provide inline/block-level extension points for plugins.
This is detailed further in the [Roles and Directives](roles-directives) section.

:::{seealso}
The [syntax token reference tables](syntax-tokens)
:::

(syntax/commonmark)=

## CommonMark

The [CommonMark syntax specification](https://spec.commonmark.org/) details the full set of syntax rules.
Here we provide a summary of most features:

Element         | Syntax
--------------- | -------------------------------------------
Heading         | `# H1` to `###### H6`
Bold            | `**bold**`
Italic          | `*italic*`
Inline Code     | `` `code` ``
Autolink        | `<https://www.example.com>`
URL Link        | `[title](https://www.example.com)`
Image           | `![alt](https://www.example.com/image.png)`
Reference Link  | `[title][link]`
Link Definition | `[link]: https://www.example.com`
Thematic break  | `---`
Blockquote      | `> quote`
Ordered List    | `1. item`
Unordered List  | `- item`
Code Fence      | opening ```` ```lang ```` to closing ```` ``` ````

(syntax/frontmatter)=

## Front Matter

This is a [YAML](https://en.wikipedia.org/wiki/YAML) block at the start of the document, as used for example in [jekyll](https://jekyllrb.com/docs/front-matter/).
The document should start with three or more `---` markers, and YAML is parsed until a closing `---` marker is found:

```yaml
---
key1: value
key2: [value1, value2]
key3:
  subkey1: value
---
```

:::{seealso}
Top-matter is also used for the [substitution syntax extension](syntax/substitutions),
and can be used to store information for blog posting (see [ablog's myst-parser support](https://ablog.readthedocs.io/en/latest/manual/markdown/)).
:::

### Setting a title

```{versionadded} 0.17.0
```

If `myst_title_to_header` is set to `True`, and a `title` key is present in the front matter,
then the title will be used as the document's header (parsed as Markdown).
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

(syntax/html_meta)=

### Setting HTML Metadata

The front-matter can contain the special key `html_meta`; a dict with data to add to the generated HTML as [`<meta>` elements](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta).
This is equivalent to using the [RST `meta` directive](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#html-metadata).

HTML metadata can also be added globally in the `conf.py` *via* the `myst_html_meta` variable, in which case it will be added to all MyST documents.
For each document, the `myst_html_meta` dict will be updated by the document level front-matter `html_meta`, with the front-matter taking precedence.

::::{tab-set}
:::{tab-item} Sphinx Configuration

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

:::{tab-item} MyST Front-Matter

```yaml
---
myst:
  html_meta:
    "description lang=en": "metadata description"
    "description lang=fr": "description des métadonnées"
    "keywords": "Sphinx, MyST"
    "property=og:locale": "en_US"
---
```

:::

:::{tab-item} RestructuredText

```restructuredtext
.. meta::
   :description lang=en: metadata description
   :description lang=fr: description des métadonnées
   :keywords: Sphinx, MyST
   :property=og:locale: en_US
```

:::

:::{tab-item} HTML Output

```html
<html lang="en">
  <head>
    <meta content="metadata description" lang="en" name="description" xml:lang="en" />
    <meta content="description des métadonnées" lang="fr" name="description" xml:lang="fr" />
    <meta name="keywords" content="Sphinx, MyST">
    <meta content="en_US" property="og:locale" />
```

:::
::::

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

:::{tip}
Comments are equivalent to the RST syntax: `.. my comment`.
:::

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

(syntax/referencing)=

## Markdown Links and Referencing

Markdown links are of the form: `[text](link)`.

If you set the configuration `myst_all_links_external = True` (`False` by default),
then all links will be treated simply as "external" links.
For example, in HTML outputs, `[text](link)` will be rendered as `<a href="link">text</a>`.

Otherwise, links will only be treated as "external" links if they are prefixed with a scheme,
configured with `myst_url_schemes` (by default, `http`, `https`, `ftp`, or `mailto`).
For example, `[example.com](https://example.com)` becomes [example.com](https://example.com).

:::{note}
The `text` will be parsed as nested Markdown, for example `[here's some *emphasised text*](https://example.com)` will be parsed as [here's some *emphasised text*](https://example.com).
:::

For "internal" links, myst-parser in Sphinx will attempt to resolve the reference to either a relative document path, or a cross-reference to a target (see [](syntax/targets)):

- `[this doc](syntax.md)` will link to a rendered source document: [this doc](syntax.md)
  - This is similar to `` {doc}`this doc <syntax>` ``; {doc}`this doc <syntax>`, but allows for document extensions, and parses nested Markdown text.
- `[example text](example.txt)` will link to a non-source (downloadable) file: [example text](example.txt)
  - The linked document itself will be copied to the build directory.
  - This is similar to `` {download}`example text <example.txt>` ``; {download}`example text <example.txt>`, but parses nested Markdown text.
- `[reference](syntax/referencing)` will link to an internal cross-reference: [reference](syntax/referencing)
  - This is similar to `` {any}`reference <syntax/referencing>` ``; {any}`reference <syntax/referencing>`, but parses nested Markdown text.
  - You can limit the scope of the cross-reference to specific [sphinx domains](sphinx:domain), by using the `myst_ref_domains` configuration.
    For example, `myst_ref_domains = ("std", "py")` will only allow cross-references to `std` and `py` domains.

Additionally, only if [](syntax/header-anchors) are enabled, then internal links to document headers can be used.
For example `[a header](syntax.md#markdown-links-and-referencing)` will link to a header anchor: [a header](syntax.md#markdown-links-and-referencing).

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

For example, see this ref: {ref}`syntax/targets`, and here's a ref back to the top of this page: {ref}`my text <syntax/core>`.

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
this page: [my text with **nested** $\alpha$ syntax](syntax/core), and here is a reference to another page (`[](../intro.md)`): [](../intro.md).

```{note}
If you wish to have the target's title inserted into your text, you can
leave the "text" section of the markdown link empty. For example, this
markdown: `[](syntax.md)` will result in: [](syntax.md).
```

(syntax/code-blocks)=
## Code syntax highlighting

Code blocks contain a language identifier, which is used to determine the language of the code.
This language is used to determine the syntax highlighting, using an available [pygments lexer](https://pygments.org/docs/lexers/).

````markdown
```python
from a import b
c = "string"
```
````

```python
from a import b
c = "string"
```

You can create and register your own lexer, using the [`pygments.lexers` entry point](https://pygments.org/docs/plugins/#register-plugins),
or within a sphinx extension, with the [`app.add_lexer` method](sphinx:sphinx.application.Sphinx.add_lexer).

Using the `myst_number_code_blocks` configuration option, you can also control whether code blocks are numbered by line.
For example, using `myst_number_code_blocks = ["typescript"]`:

```typescript
type MyBool = true | false;

interface User {
  name: string;
  id: number;
}
```

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

## Tables

Tables can be written using the standard [Github Flavoured Markdown syntax](https://github.github.com/gfm/#tables-extension-):

```md
| foo | bar |
| --- | --- |
| baz | bim |
```

| foo | bar |
| --- | --- |
| baz | bim |

Cells in a column can be aligned using the `:` character:

```md
| left | center | right |
| :--- | :----: | ----: |
| a    | b      | c     |
```

| left | center | right |
| :--- | :----: | ----: |
| a    | b      | c     |

:::{note}

Text is aligned by assigning `text-left`, `text-center`, or `text-right` to the cell.
It is then necessary for the theme you are using to include the appropriate css styling.

```html
<table class="colwidths-auto table">
  <thead>
    <tr><th class="text-left head"><p>left</p></th></tr>
  </thead>
  <tbody>
    <tr><td class="text-left"><p>a</p></td></tr>
  </tbody>
</table>
```

:::

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
Their labels **start with `^`** and can then be any alphanumeric string (no spaces), which is case-insensitive.

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
