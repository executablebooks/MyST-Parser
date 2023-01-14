---
myst:
  substitutions:
    key1: I'm a **substitution**
    key2: |
      ```{note}
      {{ key1 }}
      ```
    key3a: <img src="img/fun-fish.png" alt="fishy" width="200px">
    key3: |
      ```{image} img/fun-fish.png
      :alt: fishy
      :width: 200px
      ```
    key4: example
    confpy: sphinx `conf.py` [configuration file](inv:sphinx#usage/configuration)
---

(syntax/extensions)=

# Syntax Extensions

MyST-Parser is highly configurable, utilising the inherent "plugability" of the [markdown-it-py](inv:markdown_it#index) parser.
The following syntaxes are optional (disabled by default) and can be enabled *via* the {{ confpy }} (see also [](sphinx/config-options)).
Their goal is generally to add more *Markdown friendly* syntaxes; often enabling and rendering [markdown-it-py plugins](inv:markdown_it#md/plugins) that extend the [CommonMark specification](https://commonmark.org/).

To enable all the syntaxes explained below:

```python
myst_enable_extensions = [
    "amsmath",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "inv_link",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]
```

:::{versionchanged} 0.13.0
`myst_enable_extensions` replaces previous configuration options:
`admonition_enable`, `figure_enable`, `dmath_enable`, `amsmath_enable`, `deflist_enable`, `html_img_enable`
:::

(syntax/typography)=

## Typography

Adding `"smartquotes"` to `myst_enable_extensions` (in the {{ confpy }}) will automatically convert standard quotations to their opening/closing variants:

- `'single quotes'`: 'single quotes'
- `"double quotes"`: "double quotes"

Adding `"replacements"` to `myst_enable_extensions` (in the {{ confpy }}) will automatically convert some common typographic texts

text  | converted
----- | ----------
``(c)``, ``(C)`` | (c)
``(tm)``, ``(TM)`` | (tm)
``(r)``, ``(R)`` | (r)
``(p)``, ``(P)`` | (p)
``+-`` | +-
``...`` | ...
``?....`` | ?....
``!....`` | !....
``????????`` | ????????
``!!!!!`` | !!!!!
``,,,`` | ,,,
``--`` | --
``---`` | ---

(syntax/strikethrough)=

## Strikethrough

```{versionadded} 0.17.0
```

The `strikethrough` extension allows text within `~~` delimiters to have a strikethrough (horizontal line) placed over it.
For example, `~~strikethrough with *emphasis*~~` renders as: ~~strikethrough with *emphasis*~~.

:::{warning}
This extension is currently only supported for HTML output,
and you will need to suppress the `myst.strikethrough` warning
(see [](myst-warnings))
:::

(syntax/math)=
## Math shortcuts

Math is parsed by adding to the `myst_enable_extensions` list option, in the {{ confpy }} one or both of:

- `"dollarmath"` for parsing of dollar `$` and `$$` encapsulated math.
- `"amsmath"` for direct parsing of [amsmath LaTeX environments](https://ctan.org/pkg/amsmath).

These options enable their respective Markdown parser plugins, as detailed in the [markdown-it plugin guide](inv:markdown_it#md/plugins).

:::{versionchanged} 0.13.0
`myst_dmath_enable=True` and `myst_amsmath_enable=True` are deprecated, and replaced by `myst_enable_extensions = ["dollarmath", "amsmath"]`
:::

### Dollar delimited math

Enabling `dollarmath` will parse the following syntax:

- Inline math: `$...$`
- Display (block) math: `$$...$$`

Additionally if `myst_dmath_allow_labels=True` is set (the default):

- Display (block) math with equation label: `$$...$$ (1)`

For example, `$x_{hey}=it+is^{math}$` renders as $x_{hey}=it+is^{math}$.
This is equivalent to writing:

```md
{math}`x_{hey}=it+is^{math}`
```

:::{admonition} Escaping Dollars
:class: tip

Math can be escaped (negated) by adding a `\` before the first symbol, e.g. `\$a$` renders as \$a\$.
Escaping can also be used inside math, e.g. `$a=\$3$` renders as $a=\$3$.

Conversely `\\` will negate the escaping, so `\\$a$` renders as \\$a$.
:::

Block-level math can be specified with `$$` signs that wrap the math block you'd like to parse.
For example:

```latex
$$
    y    & = ax^2 + bx + c \\
    f(x) & = x^2 + 2xy + y^2
$$
```

becomes

$$
    y    & = ax^2 + bx + c \\
    f(x) & = x^2 + 2xy + y^2
$$

This is equivalent to the following directive:

````md
```{math}
    y    & = ax^2 + bx + c \\
    f(x) & = x^2 + 2xy + y^2
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

There are a few other options available to control dollar math parsing:

`myst_dmath_allow_space=False`, will cause inline math to only be parsed if there are no initial / final spaces, e.g. `$a$` but not `$ a$` or `$a $`.

`myst_dmath_allow_digits=False`, will cause inline math to only be parsed if there are no initial / final digits, e.g. `$a$` but not `1$a$` or `$a$2`.

These options can both be useful if you also wish to use `$` as a unit of currency.

```{versionadded} 0.14.0
`myst_dmath_double_inline` option
```

To allow display math (i.e. `$$`) within an inline context, set `myst_dmath_double_inline = True` (`False` by default).
This allows for example:

```latex
Hence, for $\alpha \in (0, 1)$,
$$
  \mathbb P (\alpha \bar{X} \ge \mu) \le \alpha;
$$
i.e., $[\alpha \bar{X}, \infty)$ is a lower 1-sided $1-\alpha$ confidence bound for $\mu$.
```

Hence, for $\alpha \in (0, 1)$,
$$
  \mathbb P (\alpha \bar{X} \ge \mu) \le \alpha;
$$
i.e., $[\alpha \bar{X}, \infty)$ is a lower 1-sided $1-\alpha$ confidence bound for $\mu$.

### Math in other block elements

Math will also work when nested in other block elements, like lists or quotes:

```md
- A list
- $$ a = 1 $$

> A block quote
> $$ a = 1 $$
```

- A list
- $$ a = 1 $$

> A block quote
> $$ a = 1 $$

### Direct LaTeX Math

Want to use [amsmath](https://ctan.org/pkg/amsmath) LaTeX directly, with no dollars?
See [the extended syntax option](syntax/amsmath).

(syntax/mathjax)=
### Mathjax and math parsing

When building HTML using the <inv:sphinx#sphinx.ext.mathjax> extension (enabled by default),
If `dollarmath` is enabled, Myst-Parser injects the `tex2jax_ignore` (MathJax v2) and  `mathjax_ignore` (MathJax v3) classes in to the top-level section of each MyST document, and adds the following default MathJax configuration:

MathJax version 2 (see [the tex2jax preprocessor](https://docs.mathjax.org/en/v2.7-latest/options/preprocessors/tex2jax.html#configure-tex2jax):

```javascript
MathJax.Hub.Config({"tex2jax": {"processClass": "tex2jax_process|mathjax_process|math|output_area"}})
```

MathJax version 3 (see [the document options](https://docs.mathjax.org/en/latest/options/document.html?highlight=ignoreHtmlClass#the-configuration-block)):

```javascript
window.MathJax = {"options": {"processHtmlClass": "tex2jax_process|mathjax_process|math|output_area"}}
```

This ensurea that MathJax processes only math, identified by the `dollarmath` and `amsmath` extensions, or specified in `math` directives.

To change this behaviour, set a custom regex, for identifying HTML classes to process, like `myst_mathjax_classes="math|myclass"`, or set `myst_update_mathjax=False` to inhibit this override and process all HTML elements.

(syntax/linkify)=
## Linkify

Adding `"linkify"` to `myst_enable_extensions` (in the {{ confpy }}) will automatically identify "bare" web URLs and add hyperlinks:

`www.example.com` -> www.example.com

To only match URLs that start with schema, such as `http://example.com`, set `myst_linkify_fuzzy_links=False`.

:::{important}
This extension requires that [linkify-it-py](https://github.com/tsutsu3/linkify-it-py) is installed.
Either directly; `pip install linkify-it-py` or *via* `pip install myst-parser[linkify]`.
:::

(syntax/substitutions)=

## Substitutions (with Jinja2)

Adding `"substitution"` to `myst_enable_extensions` (in the {{ confpy }}) will allow you to add substitutions, added in either the `conf.py` using `myst_substitutions`:

```python
myst_substitutions = {
  "key1": "I'm a **substitution**"
}
```

or at the top of the file, in the front-matter section (see [this section](syntax/frontmatter)):

````yaml
---
myst:
  substitutions:
    key1: "I'm a **substitution**"
    key2: |
      ```{note}
      {{ key1 }}
      ```
    key3: |
      ```{image} img/fun-fish.png
      :alt: fishy
      :width: 200px
      ```
    key4: example
---
````

:::{important}
Keys in the front-matter will override ones in the `conf.py`.
:::

You can use these substitutions inline or as blocks, and you can even nest substitutions in other substitutions (but circular references are prohibited):

::::{tab-set}
:::{tab-item} Markdown Input

```md
Inline: {{ key1 }}

Block level:

{{ key2 }}

| col1     | col2     |
| -------- | -------- |
| {{key2}} | {{key3}} |

```

:::

:::{tab-item} Rendered Output
Inline: {{ key1 }}

Block level:

{{ key2 }}

| col1     | col2     |
| -------- | -------- |
| {{key2}} | {{key3}} |

:::
::::

:::{important}

Substitutions will only be assessed where you would normally use Markdown, e.g. not in code blocks:

````
```
{{ key1 }}
```
````

```
{{ key1 }}
```

One should also be wary of using unsuitable directives for inline substitutions.
This may lead to unexpected outcomes.

:::

Substitution references are assessed as [Jinja2 expressions](http://jinja.palletsprojects.com) which can use [filters](https://jinja.palletsprojects.com/en/2.11.x/templates/#list-of-builtin-filters), and also contains the [Sphinx Environment](inv:sphinx#extdev/envapi) in the context (as `env`).
Therefore you can do things like:

```md
- version: {{ env.config.version }}
- docname: {{ env.docname | upper }}
- {{ "a" + "b" }}
```

- version: {{ env.config.version }}
- docname: {{ env.docname | upper }}
- {{ "a" + "b" }}

You can also change the delimiter if necessary, for example setting in the `conf.py`:

```python
myst_sub_delimiters = ["|", "|"]
```

Will parse: `|| "a" + "b" ||`.
This should be changed with care though, so as not to affect other syntaxes.

The exact logic for handling substitutions is:

1. Combine global substitutions (specified in `conf.py`) with front-matter substitutions, to create a variable context (front-matter takes priority)
2. Add the sphinx `env` to the variable context
3. Create the string content to render using Jinja2 (passing it the variable context)
4. If the substitution is inline and not a directive, render ignoring block syntaxes (like lists or block-quotes), otherwise render with all syntax rules.

### Substitutions and URLs

Substitutions cannot be directly used in URLs, such as `[a link](https://{{key4}}.com)` or `<https://{{key4}}.com>`.
However, since Jinja2 substitutions allow for Python methods to be used, you can use string formatting or replacements:

```md
{{ '[a link](https://{}.com)'.format(key4) }}

{{ '<https://myst-parser.readthedocs.io/en/latest/REPLACE.html>'.replace('REPLACE', env.docname) }}
```

{{ '[a link](https://{}.com)'.format(key4) }}

{{ '<https://myst-parser.readthedocs.io/en/latest/REPLACE.html>'.replace('REPLACE', env.docname) }}

(syntax/colon_fence)=

## Code fences using colons

By adding `"colon_fence"` to `myst_enable_extensions` (in the {{ confpy }}),
you can also use `:::` delimiters to denote code fences, instead of ```` ``` ````.

Using colons instead of back-ticks has the benefit of allowing the content to be rendered correctly, when you are working in any standard Markdown editor.
It is ideal for admonition type directives (as documented in [Directives](syntax/directives)) or tables with titles, for example:

::::::{tab-set}
:::::{tab-item} Markdown Input
```md
:::{note}
This text is **standard** _Markdown_
:::

:::{table} This is a **standard** _Markdown_ title
:align: center
:widths: grid

abc | mnp | xyz
--- | --- | ---
123 | 456 | 789
:::
```

:::::

:::::{tab-item} Rendered Output

:::{note}
This text is **standard** _Markdown_
:::

:::{table} This is a **standard** _Markdown_ title
:align: center
:widths: grid

abc | mnp | xyz
--- | --- | ---
123 | 456 | 789
:::

:::::
::::::

Similar to normal directives, these directives can also be nested:

```md
::::{important}
:::{note}
This text is **standard** _Markdown_
:::
::::
```

::::{important}
:::{note}
This text is **standard** _Markdown_
:::
::::

and also parameter options can be used:

```md
:::{admonition} This *is* also **Markdown**
:class: warning

This text is **standard** _Markdown_
:::
```

:::{admonition} This *is* also **Markdown**
:class: warning

This text is **standard** _Markdown_
:::

(syntax/admonitions)=

## Admonition directives

:::{versionchanged} 0.13.0
`myst_admonition_enable` is deprecated and replaced by `myst_enable_extensions = ["colon_fence"]` (see above).
Also, classes should now be set with the `:class: myclass` option.

Also see [](syntax/html-admonition).
:::

(syntax/header-anchors)=

## Auto-generated header anchors

The MyST Parser can automatically generate label "slugs" for header anchors so that you can reference them from markdown links.
For example, you can use header bookmark links, locally; `[](#header-anchor)`, or cross-file `[](path/to/file.md#header-anchor)`.
To achieve this, use the `myst_heading_anchors = DEPTH` configuration option, where `DEPTH` is the depth of header levels for which you wish to generate links.

For example, the following configuration in `conf.py` tells the `myst_parser` to generate labels for heading anchors for `h1`, `h2`, and `h3` level headings (corresponding to `#`, `##`, and `###` in markdown).

```python
myst_heading_anchors = 3
```

You can then insert markdown links directly to anchors that are generated from your header titles in your documentation.
For example `[](#auto-generated-header-anchors)`: [](#auto-generated-header-anchors).

The paths to other files should be relative to the current file, for example
`[**link text**](./syntax.md#core-syntax)`: [**link text**](./syntax.md#core-syntax).


### Anchor slug structure

The anchor "slugs" created aim to follow the [GitHub implementation](https://github.com/Flet/github-slugger):

- lower-case text
- remove punctuation
- replace spaces with `-`
- enforce uniqueness *via* suffix enumeration `-1`

To change the slug generation function, set `myst_heading_slug_func` in your `conf.py` to a function that accepts a string and returns a string.

### Inspect the links that will be created

You can inspect the links that will be created using the command-line tool:

```console
$ myst-anchors -l 2 docs/syntax/optional.md
<h1 id="optional-myst-syntaxes"></h1>
<h2 id="admonition-directives"></h2>
<h2 id="auto-generated-header-anchors"></h2>
<h2 id="definition-lists"></h2>
<h2 id="images"></h2>
<h2 id="markdown-figures"></h2>
<h2 id="direct-latex-math"></h2>
```

(syntax/definition-lists)=

## Definition Lists

By adding `"deflist"` to `myst_enable_extensions` (in the {{ confpy }}),
you will be able to utilise definition lists.
Definition lists utilise the [markdown-it-py deflist plugin](inv:markdown_it#md/plugins), which itself is based on the [Pandoc definition list specification](http://johnmacfarlane.net/pandoc/README.html#definition-lists).

This syntax can be useful, for example, as an alternative to nested bullet-lists:

- Term 1
  - Definition
- Term 2
  - Definition

Using instead:

```md
Term 1
: Definition

Term 2
: Definition
```

Term 1
: Definition

Term 2
: Definition

From the Pandoc documentation:

> Each term must fit on one line, which may optionally be followed by a blank line, and must be followed by one or more definitions.
> A definition begins with a colon or tilde, which may be indented one or two spaces.

> A term may have multiple definitions, and each definition may consist of one or more block elements (paragraph, code block, list, etc.)

Here is a more complex example, demonstrating some of these features:

Term *with Markdown*
: Definition [with reference](syntax/definition-lists)

  A second paragraph
: A second definition

Term 2
  ~ Definition 2a
  ~ Definition 2b

Term 3
:     A code block
: > A quote
: A final definition, that can even include images:

  <img src="img/fun-fish.png" alt="fishy" width="200px">

This was created from:

```md
Term *with Markdown*
: Definition [with reference](syntax/definition-lists)

  A second paragraph
: A second definition

Term 2
  ~ Definition 2a
  ~ Definition 2b

Term 3
:     A code block

: > A quote

: A final definition, that can even include images:

  <img src="img/fun-fish.png" alt="fishy" width="200px">
```

(syntax/tasklists)=
## Task Lists

By adding `"tasklist"` to `myst_enable_extensions` (in the {{ confpy }}),
you will be able to utilise task lists.
Task lists utilise the [markdown-it-py tasklists plugin](inv:markdown_it#md/plugins),
and are applied to markdown list items starting with `[ ]` or `[x]`:

```markdown
- [ ] An item that needs doing
- [x] An item that is complete
```

- [ ] An item that needs doing
- [x] An item that is complete

(syntax/fieldlists)=
## Field Lists

```{versionadded} 0.16.0
```

Field lists are mappings from field names to field bodies,
based on the [reStructureText syntax](https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#field-lists).

````md
:name only:
:name: body
:*Nested syntax*: Both name and body may contain **nested syntax**.
:Paragraphs: Since the field marker may be quite long, the second
   and subsequent lines of a paragraph do not have to line up
   with the first line.
:Alignment 1: If the field body starts on the first line...

              Then the entire field body must be indented the same.
:Alignment 2:
  If the field body starts on a subsequent line...

  Then the indentation is always two spaces.
:Blocks:

  As well as paragraphs, any block syntaxes may be used in a field body:

  - Me
  - Myself
  - I

  ```python
  print("Hello, world!")
  ```
````

:name only:
:name: body
:*Nested syntax*: Both name and body may contain **nested syntax**.
:Paragraphs: Since the field marker may be quite long, the second
   and subsequent lines of a paragraph do not have to line up
   with the first line.
:Alignment 1: If the field body starts on the first line...

              Then the entire field body must be indented the same.
:Alignment 2:
  If the field body starts on a subsequent line...

  Then the indentation is always two spaces.
:Blocks:

  As well as paragraphs, any block syntaxes may be used in a field body:

  - Me
  - Myself
  - I

  ```python
  print("Hello, world!")
  ```

A prominent use case of field lists is for use in API docstrings, as used in [Sphinx's docstring renderers](inv:sphinx#python-domain):

````md
```{py:function} send_message(sender, priority)

Send a message to a recipient

:param str sender: The person sending the message
:param priority: The priority of the message, can be a number 1-5
:type priority: int
:return: the message id
:rtype: int
:raises ValueError: if the message_body exceeds 160 characters
```
````

```{py:function} send_message(sender, priority)

Send a message to a recipient

:param str sender: The person sending the message
:param priority: The priority of the message, can be a number 1-5
:type priority: int
:return: the message id
:rtype: int
:raises ValueError: if the message_body exceeds 160 characters
```

:::{note}
Currently `sphinx.ext.autodoc` does not support MyST, see [](howto/autodoc).
:::

(syntax/attributes)=
## Inline attributes

:::{versionadded} 0.19
This feature is in *beta*, and may change in future versions.
It replace the previous `attrs_image` extension, which is now deprecated.
:::

By adding `"attrs_inline"` to `myst_enable_extensions` (in the {{ confpy }}),
you can enable parsing of inline attributes after certain inline syntaxes.
This is adapted from [djot inline attributes](https://htmlpreview.github.io/?https://github.com/jgm/djot/blob/master/doc/syntax.html#inline-attributes),
and also related to [pandoc bracketed spans](https://pandoc.org/MANUAL.html#extension-bracketed_spans).

Attributes are specified in curly braces after the inline syntax.
Inside the curly braces, the following syntax is recognised:

- `.foo` specifies `foo` as a class.
  Multiple classes may be given in this way; they will be combined.
- `#foo` specifies `foo` as an identifier.
  An element may have only one identifier;
  if multiple identifiers are given, the last one is used.
- `key="value"` or `key=value` specifies a key-value attribute.
    Quotes are not needed when the value consists entirely of
    ASCII alphanumeric characters or `_` or `:` or `-`.
    Backslash escapes may be used inside quoted values.
    **Note** only certain keys are supported, see below.
- `%` begins a comment, which ends with the next `%` or the end of the attribute (`}`).

For example, the following Markdown:

```md

- [A span of text with attributes]{#spanid .bg-warning},
  {ref}`a reference to the span <spanid>`

- `A literal with attributes`{#literalid .bg-warning},
  {ref}`a reference to the literal <literalid>

- An autolink with attributes: <https://example.com>{.bg-warning title="a title"}

- [A link with attributes](syntax/attributes){#linkid .bg-warning},
  {ref}`a reference to the link <linkid>`

- ![An image with attribute](img/fun-fish.png){#imgid .bg-warning w=100px align=center}
  {ref}`a reference to the image <imgid>`

```

will be parsed as:

- [A span of text with attributes]{#spanid .bg-warning},
  {ref}`a reference to the span <spanid>`

- `A literal with attributes`{#literalid .bg-warning},
  {ref}`a reference to the literal <literalid>`

- An autolink with attributes: <https://example.com>{.bg-warning title="a title"}

- [A link with attributes](syntax/attributes){#linkid .bg-warning},
  {ref}`a reference to the link <linkid>`

- ![An image with attribute](img/fun-fish.png){#imgid .bg-warning w="100px" align=center}
  {ref}`a reference to the image <imgid>`

### key-value attributes

`id` and `class` are supported for all inline syntaxes,
but only certain key-value attributes are supported for each syntax.

For **literals**, the following attributes are supported:

- `language`/`lexer`/`l` defines the syntax lexer,
  e.g. `` `a = "b"`{l=python} `` is displayed as `a = "b"`{l=python}.
  Note, this is only supported in `sphinx >= 5`.

For **images**, the following attributes are supported (equivalent to the `image` directive):

- `width`/`w` defines the width of the image (in `%`, `px`, `em`, `cm`, etc)
- `height`/`h` defines the height of the image (in `px`, `em`, `cm`, etc)
- `align`/`a` defines the scale of the image (`left`, `center`, or `right`)

(syntax/images)=

## HTML Images

MyST provides a few different syntaxes for including images in your documentation, as explained below.

The first is the standard Markdown syntax:

```md
![fishy](img/fun-fish.png)
```

![fishy](img/fun-fish.png)

This will correctly copy the image to the build folder and will render it in all output formats (HTML, TeX, etc).
However, it is limited in the configuration that can be applied, for example setting a width.

As discussed [above](syntax/directives), MyST allow for directives to be used such as `image` and `figure` (see {ref}`the sphinx documentation <sphinx:rst-primer>`):

````md
```{image} img/fun-fish.png
:alt: fishy
:class: bg-primary
:width: 200px
:align: center
```
````

```{image} img/fun-fish.png
:alt: fishy
:class: bg-primary mb-1
:width: 200px
```

Additional options can now be set, however, in contrast to the Markdown syntax, this syntax will not show the image in common Markdown viewers (for example when the files are viewed on GitHub).

The final option is directly using HTML, which is also parsed by MyST.
This is usually a bad option, because the HTML is treated as raw text during the build process and so sphinx will not recognise that the image file is to be copied, and will not output the HTML into non-HTML output formats.

HTML parsing to the rescue!

By adding `"html_image"` to `myst_enable_extensions` (in the {{ confpy }}),
MySt-Parser will attempt to convert any isolated `img` tags (i.e. not wrapped in any other HTML) to the internal representation used in sphinx.

```html
<img src="img/fun-fish.png" alt="fishy" width="200px">
<img src="img/fun-fish.png" alt="fishy" width="200px" class="bg-primary">
```

<img src="img/fun-fish.png" alt="fishy" width="200px">
<img src="img/fun-fish.png" alt="fishy" width="200px" class="bg-primary">

Allowed attributes are equivalent to the `image` directive: src, alt, class, width, height and name.
Any other attributes will be dropped.

HTML image can also be used inline!

I'm an inline image: <img src="img/fun-fish.png" height="20px">

(syntax/figures)=

## Markdown Figures

By adding `"colon_fence"` to `myst_enable_extensions` (in the {{ confpy }}),
we can combine the above two extended syntaxes,
to create a fully Markdown compliant version of the `figure` directive named `figure-md`.

:::{versionchanged} 0.13.0
`myst_figure_enable` with the `figure` directive is deprecated and replaced by `myst_enable_extensions = ["colon_fence"]` and `figure-md`.
:::

The figure block must contain **only** two components; an image, in either Markdown or HTML syntax, and a single paragraph for the caption.

The title is optional and taken as the reference target of the figure:

```md
:::{figure-md} fig-target
:class: myclass

<img src="img/fun-fish.png" alt="fishy" class="bg-primary mb-1" width="200px">

This is a caption in **Markdown**
:::
```

:::{figure-md} fig-target
:class: myclass

<img src="img/fun-fish.png" alt="fishy" class="bg-primary mb-1" width="200px">

This is a caption in **Markdown**
:::

As we see here, the target we set can be referenced:

```md
[Go to the fish!](fig-target)
```

[Go to the fish!](fig-target)

(syntax/html-admonition)=

## HTML Admonitions

By adding `"html_admonition"` to `myst_enable_extensions` (in the {{ confpy }}),
you can enable parsing of `<div class="admonition">` HTML blocks.
These blocks will be converted internally to Sphinx admonition directives, and so will work correctly for all output formats.
This is helpful when you care about viewing the "source" Markdown, such as in Jupyter Notebooks.

If the first element within the `div` is `<div class="title">` or `<p class="title">`, then this will be set as the admonition title.
All internal text (and the title) will be parsed as MyST-Markdown and all classes and an optional name will be passed to the admonition:

```html
<div class="admonition note" name="html-admonition" style="background: lightgreen; padding: 10px">
<p class="title">This is the **title**</p>
This is the *content*
</div>
```

<div class="admonition note" name="html-admonition" style="background: lightgreen; padding: 10px">
<div class="title">This is the **title**</div>
This is the *content*
</div>

During the Sphinx render, both the `class` and `name` attributes will be used by Sphinx, but any other attributes like `style` will be discarded.

:::{warning}
There can be no empty lines in the block, otherwise they will be read as two separate blocks.
If you want to use multiple paragraphs then they can be enclosed in `<p>`:

```html
<div class="admonition note">
<p>Paragraph 1</p>
<p>Paragraph 2</p>
</div>
```

<div class="admonition note">
<p>Paragraph 1</p>
<p>Paragraph 2</p>
</div>

:::

You can also nest HTML admonitions:

```html
<div class="admonition">
<p>Some **content**</p>
  <div class="admonition tip">
  <div class="title">A *title*</div>
  <p>Paragraph 1</p>
  <p>Paragraph 2</p>
  </div>
</div>
```

<div class="admonition">
<p>Some **content**</p>
  <div class="admonition tip">
  <div class="title">A *title*</div>
  <p>Paragraph 1</p>
  <p>Paragraph 2</p>
  </div>
</div>

(syntax/amsmath)=

## Direct LaTeX Math

By adding `"amsmath"` to `myst_enable_extensions` (in the {{ confpy }}),
you can enable direct parsing of [amsmath](https://ctan.org/pkg/amsmath) LaTeX equations.
These top-level math environments will then be directly parsed:

> equation, multline, gather, align, alignat, flalign, matrix, pmatrix, bmatrix, Bmatrix, vmatrix, Vmatrix, eqnarray.

As expected, environments ending in `*` will not be numbered, for example:

```latex
\begin{gather*}
a_1=b_1+c_1\\
a_2=b_2+c_2-d_2+e_2
\end{gather*}

\begin{align}
a_{11}& =b_{11}&
  a_{12}& =b_{12}\\
a_{21}& =b_{21}&
  a_{22}& =b_{22}+c_{22}
\end{align}
```

\begin{gather*}
a_1=b_1+c_1\\
a_2=b_2+c_2-d_2+e_2
\end{gather*}

\begin{align}
a_{11}& =b_{11}&
  a_{12}& =b_{12}\\
a_{21}& =b_{21}&
  a_{22}& =b_{22}+c_{22}
\end{align}

:::{note}
`\labels` inside the environment are not currently identified, and so cannot be referenced.
We hope to implement this in a future update (see [executablebooks/MyST-Parser#202](https://github.com/executablebooks/MyST-Parser/issues/202))!
:::

:::{important}
See also [how Mathjax is configured with MyST-Parser](syntax/mathjax).
:::

This syntax will also work when nested in other block elements, like lists or quotes:

```md
- A list
- \begin{gather*}
  a_1=b_1+c_1\\a_2=b_2+c_2-d_2+e_2
  \end{gather*}

> A block quote
> \begin{gather*}
  a_1=b_1+c_1\\a_2=b_2+c_2-d_2+e_2
  \end{gather*}
```

- A list
- \begin{gather*}
  a_1=b_1+c_1\\a_2=b_2+c_2-d_2+e_2
  \end{gather*}

> A block quote
> \begin{gather*}
  a_1=b_1+c_1\\a_2=b_2+c_2-d_2+e_2
  \end{gather*}
