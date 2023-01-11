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
This is equivalent to using the [meta directive](inv:sphinx#html-meta).

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

### CommonMark link format

CommonMark links come in three forms ([see the spec](https://spec.commonmark.org/0.30/#links)):

*Autolinks* are [URIs][uri] surrounded by `<` and `>`, which must always have a scheme:

```md
<scheme:path?query#fragment>
```

*Inline links* allow for optional explicit text and titles (in HTML titles are rendered as tooltips):

```md
[Explicit *Markdown* text](destination "optional explicit title")
```

or, if the destination contains spaces,

```md
[Explicit *Markdown* text](<a destination> "optional explicit title")
```

*Reference links* define the destination separately in the document, and can be used multiple times:

```md
[Explicit *Markdown* text][label]
[Another link][label]

[label]: destination "optional explicit title"
```

[uri]: https://en.wikipedia.org/wiki/Uniform_Resource_Identifier
[url]: https://en.wikipedia.org/wiki/URL

### Default destination resolution

The destination of a link can resolve to either an **external** target, such as a [URL] to another website,
or an **internal** target, such as a file, heading or figure within the same project.

By default, MyST will resolve link destinations according to the following rules:

1. All autolinks will be treated as external [URL] links.

2. Destinations beginning with  `http:`, `https:`, `ftp:`, or `mailto:` will be treated as external [URL] links.

3. Destinations which point to a local file path are treated as links to that file.
   - The path must be relative and in [POSIX format](https://en.wikipedia.org/wiki/Path_(computing)#POSIX_and_Unix_paths) (i.e. `/` separators).
   - If the path is to another source file in the project (e.g. a `.md` or `.rst` file),
    then the link will be to the initial heading in that file or,
    if the path is appended by a `#target`, to the heading "slug" in that file.
   - If the path is to a non-source file (e.g. a `.png` or `.pdf` file),
    then the link will be to the file itself, e.g. to download it.

4. Destinations beginning with `#` will be treated as a link to a heading "slug" in the same file.
   - This requires the `myst_heading_anchors` configuration be set.
   - For more details see [](syntax/header-anchors).

5. All other destinations are treated as internal references, which can link to any type of target within the project (see [](syntax/targets)).

Here are some examples:

:::{list-table}
:header-rows: 1

* - Type
  - Syntax
  - Rendered

* - Autolink
  - `<https://example.com>`
  - <https://example.com>

* - External URL
  - `[example.com](https://example.com)`
  - [example.com](https://example.com)

* - Internal source file
  - `[Source file](syntax.md)`
  - [Source file](syntax.md)

* - Internal non-source file
  - `[Non-source file](example.txt)`
  - [Non-source file](example.txt)

* - Local heading
  - `[Heading](#markdown-links-and-referencing)`
  - [Heading](#markdown-links-and-referencing)

* - Heading in another file
  - `[Heading](optional.md#auto-generated-header-anchors)`
  - [Heading](optional.md#auto-generated-header-anchors)

:::

### Customising destination resolution

You can customise the default destination resolution rules by setting the following [configuration options](../configuration.md):

`myst_all_links_external` (default: `False`)
:   If `True`, then all links will be treated as external links.

`myst_url_schemes` (default: `["http", "https", "ftp", "mailto"]`)
: A list of [URL] schemes which will be treated as external links.

`myst_ref_domains` (default: `[]`)
: A list of [sphinx domains](inv:sphinx#domain) which will be allowed for internal links.
  For example, `myst_ref_domains = ("std", "py")` will only allow cross-references to `std` and `py` domains.
  If the list is empty, then all domains will be allowed.

(syntax/inv_links)=
### Cross-project (inventory) links

:::{versionadded} 0.19
This functionality is currently in *beta*.
It is intended that eventually it will be part of the core syntax.
:::

Each Sphinx HTML build creates a file named `objects.inv` that contains a mapping from referenceable objects to [URIs][uri] relative to the HTML set’s root.
Each object is uniquely identified by a `domain`, `type`, and `name`.
As well as the relative location, the object can also include implicit `text` for the reference (like the text for a heading).

You can use the `myst-inv` command line tool (installed with `myst_parser`) to visualise and filter any remote URL or local file path to this inventory file (or its parent):

```yaml
# $ myst-inv https://www.sphinx-doc.org/en/master -n index
name: Sphinx
version: 6.2.0
base_url: https://www.sphinx-doc.org/en/master
objects:
  rst:
    role:
      index:
        loc: usage/restructuredtext/directives.html#role-index
        text: null
  std:
    doc:
      index:
        loc: index.html
        text: Welcome
```

To load external inventories into your Sphinx project, you must load the [`sphinx.ext.intersphinx` extension](inv:sphinx#usage/*/intersphinx), and set the `intersphinx_mapping` configuration option.
Then also enable the `inv_link` MyST extension e.g.:

```python
extensions = ["myst_parser", "sphinx.ext.intersphinx"]
intersphinx_mapping = {
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
}
myst_enable_extensions = ["inv_link"]
```

:::{dropdown} Docutils configuration

Use the `docutils.conf` configuration file, for more details see [](myst-docutils).

```ini
[general]
myst-inventories:
  sphinx: ["https://www.sphinx-doc.org/en/master", null]
myst-enable-extensions: inv_link
```

:::

you can then reference inventory objects by prefixing the `inv` schema to the destination [URI]: `inv:key:domain:type#name`.

`key`, `domain` and `type` are optional, e.g. for `inv:#name`, all inventories, domains and types will be searched, with a [warning emitted](myst-warnings) if multiple matches are found.

Additionally, `*` is a wildcard which matches zero or characters, e.g. `inv:*:std:doc#a*` will match all `std:doc` objects in all inventories, with a `name` beginning with `a`.
Note, to match to a literal `*` use `\*`.

Here are some examples:

:::{list-table}
:header-rows: 1

* - Type
  - Syntax
  - Rendered

* - Autolink, full
  - `<inv:sphinx:std:doc#index>`
  - <inv:sphinx:std:doc#index>

* - Link, full
  - `[Sphinx](inv:sphinx:std:doc#index)`
  - [Sphinx](inv:sphinx:std:doc#index)

* - Autolink, no type
  - `<inv:sphinx:std#index>`
  - <inv:sphinx:std#index>

* - Autolink, no domain
  - `<inv:sphinx:*:doc#index>`
  - <inv:sphinx:*:doc#index>

* - Autolink, only name
  - `<inv:#*.Sphinx>`
  - <inv:#*.Sphinx>

:::

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

They can then be referred to with the
[`ref` inline role](inv:sphinx#ref-role):

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

is equivalent to using the [`any` inline role](inv:sphinx#any-role):

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
or within a sphinx extension, with the [`app.add_lexer` method](inv:sphinx#*.Sphinx.add_lexer).

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

    Plus any subsequent unindented lines,
that are not separated by a blank line

This is not part of the footnote.

````{important}
Although footnote references can be used just fine within directives, e.g.[^myref],
it is recommended that footnote definitions are not set within directives,
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
