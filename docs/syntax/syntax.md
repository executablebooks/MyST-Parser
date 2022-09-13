(syntax/core)=

# Core Syntax

## Introduction

MyST is a strict superset of the [CommonMark syntax specification](https://spec.commonmark.org/).
It adds features focussed on scientific and technical documentation authoring, as detailed below.

In addition, the roles and directives syntax provide inline/block-level extension points for plugins.
This is detailed further in the [Roles and Directives](#roles-directives) section.

:::{seealso}
The [syntax token reference tables](#syntax-tokens)
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
Top-matter is also used for the [substitution syntax extension](#syntax/substitutions),
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
This is equivalent to using the [RST `meta` directive](myst:sphinx#html-meta).

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

## Links and Referencing

CommonMark links come in three forms ([see the spec](https://spec.commonmark.org/0.30/#links)):

*Autolinks* are [URIs][uri] surrounded by `<` and `>`:

```md
<scheme:path?query#fragment>
```

*Inline links* allow for optional explicit text and titles (in HTML titles are rendered as tooltips):

```md
[Explicit *Markdown* text](destination "optional explicit title")
```

or, if the destination contains spaces,

```md
[text](<a destination>)
```

*Reference links* define the destination separately in the document, and can be used multiple times:

```md
[Explicit *Markdown* text][label]

[label]: destination "optional explicit title"
```

MyST, supports the following destination types:

|     Link Type      |            Auto            |          Inline           | Single Page[^sp] |
| :----------------- | :------------------------- | :------------------------ | :--------------: |
| External URL       | `<https://example.com>`    | `[](https://example.com)` |        ✅         |
| Local file path    | `<path:file.txt>`          | `[](file.txt)`            |        ❌         |
| Project document   | `<project:file.md>`        | `[](file.md)`             |        ❌         |
| Target in document | `<project:target.md#file>` | `[](file.md#target)`      |        ❌         |
| Target in project  | `<project:#target>`        | `[](#target)`             |     ✅[^hash]     |
| Cross-project      | `<myst:key#target>`        | `[](myst:key#target)`     |        ❌         |

[^sp]: Whether this link type is supported in [single page builds](../docutils.md),
       otherwise a `myst.xref_unsupported` warning will be emitted, and the text rendered without a link.
[^hash]: Single page builds will try to resolve the target, only if it is in the current document, otherwise a `myst.xref_missing` warning will be emitted, and the text rendered without a link.

The `path`, `project` and `myst` scheme are used to indicate that the link should be resolved by MyST specific logic, as described below.
Its format follows standard [URI][uri] syntax:

```
URI = scheme ":" type ["?" query] "#" fragment
```

:::{versionchanged} 0.19.0
- The `path:`, `project:`, `myst:` scheme was introduced
- `[text](#target)` syntax replaces the previous `[text](target)` syntax.
  On upgrading, you may now see [`myst.invalid_uri` warnings](#myst-warnings).
- `[text](?name#target)` syntax replaces the `myst_ref_domains` config.
- `[text](#target)` will now refer to any project reference, not just heading anchors.
:::

[uri]: https://en.wikipedia.org/wiki/Uniform_Resource_Identifier

(syntax/referencing/external)=
### External URLs

External [Uniform Resource Locator (URL)](https://en.wikipedia.org/wiki/URL) are direct links to other websites.
They are recognised by the presence of a known URL scheme (`scheme:...`).
This can be configured using the [`myst_url_schemes` configuration variable](../configuration.md),
and by default is  `http`, `https`, `ftp`, or `mailto`.

| Examples |                                              |                                            |
| :------- | :------------------------------------------- | :----------------------------------------- |
| Auto     | `<https://example.com>`                      | <https://example.com>                      |
| Inline   | `[Some *text*](https://example.com "title")` | [Some *text*](https://example.com "title") |

Note, if you set the configuration `myst_all_links_external = True` (`False` by default),
then all links will be treated simply as external URLs.

(syntax/referencing/paths)=
### Paths to local files and documents

If the destination can be resolved as to a file on the local filesystem,
then it will be treated as a link to a local file.

File paths should be in the POSIX format (i.e. `/` as the path separator).
If the path starts with a `/`, then it will be treated as a path relative to the root of the project,
otherwise it will be treated as a path relative to the current file.

If the file is another source document in the project (e.g. another Markdown file),
then the link will be resolved to that location in the build output.
If no explicit link text is given, the link text will be the title of the given document.

If the file is a non-source document, then the referenced file will be marked for inclusion in the build output.
The rendered link will be the path to the file in the build output.
Note, that such links will generally only be rendered in HTML builds.

To be more explicit, you can use the `project:` and `path:` scheme to indicate that the link should always be treated as a document or file respectively.

| Examples |                                      |                                    |
| :------- | :----------------------------------- | :--------------------------------- |
| File     | `[Some *text*](example.txt "title")` | [Some *text*](example.txt "title") |
|          | `<path:example.txt>`                 | <path:example.txt>                 |
|          | `<path:/syntax/example.txt>`         | <path:/syntax/example.txt>         |
| Document | `[Some *text*](optional.md "title")` | [Some *text*](optional.md "title") |
|          | `<project:optional.md>`              | <project:optional.md>              |
|          | `<project:/syntax/optional.md>`      | <project:/syntax/optional.md>      |

(syntax/targets)=
(syntax/referencing/myst-local)=
### Document-specific targets

MyST allows for explicit reference targets to be defined in the document.

The most general way to do this is using the `(target)=` syntax.
This can be placed above any content block, such as headings, paragraphs, or code blocks, to allow them to be referenced.
For example:

````md
(code-block-1)=
```python
print("Hello World!")
```
````

Allows the code block to be referenced by the `code-block-1` name.

(code-block-1)=
```python
print("Hello World!")
```

Additionally, many [directives](#syntax/directives) include a `name` option, to define the target.
For example:

````md
```{code-block} python
:name: code-block-2
:caption: A code block
print("Hello World!")
```
````

Allows the code block to be referenced by the `code-block-2` name.

```{code-block} python
:name: code-block-2
:caption: A code block
print("Hello World!")
```

To reference these targets only within the same document, use the `project:.#target` URI, or the shorthand `.#target` syntax.

When targetting certain block types, such as headings or directives with captions, if no explicit text is given, then the text will be derived from the title or caption text. In these instances, the auto-link format can be used.

| Examples |                                         |                                       |
| :------- | :-------------------------------------- | :------------------------------------ |
| Inline   | `[Some *text*](.#code-block-1 "title")` | [Some *text*](.#code-block-1 "title") |
| Auto     | `<project:.#code-block-2>`              | <project:.#code-block-2>              |

If you wish to reference a target specifically in another document, use the `project:path/to/file.md#target` URI, or the shorthand `path/to/file.md#target` syntax.
As per the [document links](#syntax/referencing/paths), if the path starts with a `/`, then it will be treated as a path relative to the root of the project.

| Examples |                                                   |                                                 |
| :------- | :------------------------------------------------ | :---------------------------------------------- |
| Inline   | `[text](optional.md#syntax/extensions)`           | [text](optional.md#syntax/extensions)           |
|          | `[text](/syntax/optional.md#syntax/extensions)`   | [text](/syntax/optional.md#syntax/extensions)   |
| Auto     | `<project:optional.md#syntax/extensions>`         | <project:optional.md#syntax/extensions>         |
|          | `<project:/syntax/optional.md#syntax/extensions>` | <project:/syntax/optional.md#syntax/extensions> |

### Auto-generating heading targets

To mimic the behaviour of platforms such as [GitHub][gh-section-links], MyST allows for the auto-generation of targets for headings.

See the <project#syntax/header-anchors> section for more details.

[gh-section-links]: https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#section-links

(syntax/referencing/project)=
### Project-wide targets

As well as generating reference targets for content blocks and directives, sphinx (and its extensions) may also generate targets for a range of other objects in the project, such as software package APIs.
These are collated into an *inventory* of targets, scoped by **domain** and **object type**.

To explore the inventory of targets in your project, see <project:#syntax/referencing/builder>.
This may generate a YAML resembling the following:

```yaml
name: MyST Parser
version: 0.18.0
objects:
  py:
    class:
      myst_parser.parsers.sphinx_.MystParser:
        docname: api/reference
        id: myst_parser.parsers.sphinx_.MystParser
  std:
    label:
      api/directive:
        docname: api/reference
        id: api-directive
        text: Directive and role processing
    doc:
      api/reference:
        docname: api/reference
        id: ''
        text: Python API
```

To reference a project wide target, in any domain or object type, use the `project:#target` URI, or the shorthand `#target` syntax.
Without a specific path, these references will first be searched for in the current document, then only if not found there, in the project-wide inventory.

If no explicit text is set then either the `text` will be used, if present, or the name of the target.

If you wish the target to match any name with a particular ending, prepend by `*`.
This is useful for long API names, where you may wish to specify the class, but not the module.

| Examples |                               |                             |
| :------- | :---------------------------- | :-------------------------- |
| Inline   | `[text](#api/reference)`      | [text](#api/reference)      |
| Auto     | `<project:#api/reference>`    | <project:#api/reference>    |
| Match end  | `<project:#*.MystParser>` | <project:#*.MystParser> |

(syntax/referencing/filter)=
### Filtering target matches

If a referenced target is present in multiple domains and/or object types, then you will see a warning such as:

```
<src>/test.md:2: WARNING: Multiple matches found for target '*:*:duplicate': 'std:label:duplicate','std:term:duplicate' [myst.xref_duplicate]
```

In this case, you can use the query string to filter matches by `domain:object_type`.
Use `*` to match any value, e.g. `*:term` will match `term` in any domain.

|                 Examples                  |                                         |
| :---------------------------------------- | :-------------------------------------- |
| `[text](?std:label#api/main)` | [text](?std:label#api/main) |

(section:ref)=
### Referencing numbered objects

MyST allows for the enumeration of objects, such as sections, figures, tables, equations, and code blocks, and the referencing of these objects by their number.

To enable numbering of objects, use the [`numfig` configuration option](myst:sphinx#numfig).

```python
numfig = True
```

If there is no section numbering, then each object type will be numbered independently, in consecutive order across the whole project.
To number sections, the `toctree` directive that contains the page must have the `numbered` flag set.

````md
```{toctree}
:numbered:

page.md
```
````

Object numbering can the be controlled by the [`numfig_secnum_depth` configuration option](myst:sphinx#numfig_secnum_depth).

```python
numfig_secnum_depth = 2
```

This will restart object numbering at each second level section heading, and will prepend the section number to the object number, e.g. `h1.h2.o`.

Figures, tables and code blocks will be numbered only if they have a caption.
The prefix for the caption can be set using the [`numfig_format` configuration option](myst:sphinx#numfig_format), where `%s` is replaced with the number.

```python
numfig_format = {
    "figure": "Fig. %s",
    "table": "Table %s",
    "code-block": "Listing %s",
}
```

Below are some examples of numbered objects:


::::{grid} 2
:gutter: 1

:::{grid-item-card}
````md
```{figure} img/fun-fish.png
:name: figure:ref

Caption for the figure
```
````
:::
:::{grid-item-card}
```{figure} img/fun-fish.png
:name: figure:ref
:height: 100px

Caption for the figure
```
:::

:::{grid-item-card}
````md
```{code-block} python
:caption: Caption for the code block
:name: code:ref

a = 1
```
````
:::
:::{grid-item-card}
```{code-block} python
:caption: Caption for the code block
:name: code:ref

a = 1
```
:::

:::{grid-item-card}
````md
```{table} Caption for the table
:name: table:ref

a  | b
-- | --
c  | d
```
````
:::
:::{grid-item-card}
```{table} Caption for the table
:name: table:ref

a  | b
-- | --
c  | d
```
:::

:::{grid-item-card}
````md
```{math}
:label: eq:ref
a = 1
```
````
:::
:::{grid-item-card}
```{math}
:label: eq:ref
a = 1
```
:::

::::

To refer to the number or title/caption of a numbered object, you must first enable placeholder replacements.

```python
myst_link_placeholders = True
```

You can also set prefixes for enumerable types, using:

```python
myst_link_prefixes = {
    "equation": "eq.",
    "table": "tbl.",
    "figure": "fig.",
    "code-block": "code",
}
```

You can then use these placeholders in the link text:

- `{name}`: the implicit text of the object
- `{number}`: the number of the object
- `{prefix}`: the prefix of the enumerable type
- `{Prefix}`: capitalized prefix of the enumerable type

|                   Examples                   |                                            |
| :------------------------------------------- | :----------------------------------------- |
| `[{Prefix} {number} *"{name}"*](#section:ref)` | [{Prefix} {number} *"{name}"*](#section:ref) |
| `[{Prefix} {number} *"{name}"*](#figure:ref)`  | [{Prefix} {number} *"{name}"*](#figure:ref)  |
| `[{Prefix} {number} *"{name}"*](#code:ref)`    | [{Prefix} {number} *"{name}"*](#code:ref)    |
| `[{Prefix} {number} *"{name}"*](#table:ref)`   | [{Prefix} {number} *"{name}"*](#table:ref)   |
| `[{Prefix} {number}](#eq:ref)`                 | [{Prefix} {number}](#eq:ref)                 |


(syntax/referencing/myst-inv)=
### Cross-project (inventory) targets

For HTML builds, the inventory that is generated for the project, is also written to a file called `objects.inv`,
and contains the "endpoints" for all the targets in the project, which can be combined with the base URL of the project to create a full URL to the target.

Any HTML site then built with Sphinx should contain this file at the root of the site.
You can export this file to a readable YAML, using the `myst-inv` command line tool, pointing to either a local file or remote URL:

```yaml
# $ myst-inv -d "py" -o "module" -n "datetime"  https://docs.python.org/3.7/objects.inv
name: Python
version: '3.7'
objects:
  py:
    module:
      datetime:
        loc: library/datetime.html#module-datetime
        disp: '-'
```

To load external inventories into your Sphinx project, you must load the [`sphinx.ext.intersphinx` extension](myst:sphinx#usage/extensions/intersphinx), and set the `intersphinx_mapping` configuration option, e.g.:

```python
extensions = ["myst_parser", "sphinx.ext.intersphinx"]
intersphinx_mapping = {
    "python": ("https://docs.python.org/3.7", None),
}
```

You can then use `myst:key#target` to reference targets in an external inventory, in a similar fashion to the [project-wide targets](#syntax/referencing/project).
If a key is not specified, then all inventories will be searched.

See also [](#syntax/referencing/filter) for filtering matches by domain and object type.

| Examples |                                |                              |
| :------- | :----------------------------- | :--------------------------- |
| Inline   | `[text](myst:python#datetime)` | [text](myst:python#datetime) |
| Auto     | `<myst:python#datetime>`       | <myst:python#datetime>       |
| All      | `<myst:#datetime>`             | <myst:#datetime>             |
| Filter   | `<myst:python?py:*#datetime>`       | <myst:python?py:*#datetime>             |

(syntax/referencing/builder)=
### Exploring references in a project

As well as the `myst-inv` command-line tool, `myst-parser` also provides the `myst_refs` builder, which can be used to explore references available to a projects.

Running: `sphinx-build -b myst_refs docs/ docs/_build/myst_refs` will generate a folder containing YAML files, showing targets available for the `path:`, `project:` and `myst:` URI schemes.

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
or within a sphinx extension, with the [`app.add_lexer` method](myst:sphinx#sphinx.application.Sphinx.add_lexer).

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
See the [extended image syntax guide](#syntax/images).

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
