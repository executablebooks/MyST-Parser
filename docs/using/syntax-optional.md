---
substitutions:
  key1: I'm a **substitution**
  key2: |
    ```{note}
    {{ key1 }}
    ```
  key3: <img src="img/fun-fish.png" alt="fishy" width="200px">
---

(syntax/optional)=

# Optional MyST Syntaxes

MyST-Parser is highly configurable, utilising the inherent "plugability" of the [markdown-it-py](markdown_it:index) parser.
The following syntaxes are optional (disabled by default) and can be enabled *via* the sphinx `conf.py` (see also [](intro/config-options)).
Their goal is generally to add more *Markdown friendly* syntaxes; often enabling and rendering [markdown-it-py plugins](markdown_it:md/plugins) that extend the [CommonMark specification](https://commonmark.org/).

To enable all the syntaxes explained below:

```python
myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "substitution"
]
```

:::{important}
`myst_enable_extensions` replaces previous configuration options:
`admonition_enable`, `figure_enable`, `dmath_enable`, `amsmath_enable`, `deflist_enable`, `html_img_enable`
:::

(syntax/typography)=

## Typography

Adding `"smartquotes"` to `myst_enable_extensions` (in the sphinx `conf.py` [configuration file](https://www.sphinx-doc.org/en/master/usage/configuration.html)) will automatically convert standard quotations to their opening/closing variants:

- `'single quotes'`: 'single quotes'
- `"double quotes"`: "double quotes"

Adding `"replacements"` to `myst_enable_extensions` (in the sphinx `conf.py` [configuration file](https://www.sphinx-doc.org/en/master/usage/configuration.html)) will automatically convert some common typographic texts

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

(syntax/linkify)=

## Linkify

Adding `"linkify"` to `myst_enable_extensions` (in the sphinx `conf.py` [configuration file](https://www.sphinx-doc.org/en/master/usage/configuration.html)) will automatically identify "bare" web URLs and add hyperlinks:

`www.example.com` -> www.example.com

:::{important}
This extension requires that [linkify-it-py](https://github.com/tsutsu3/linkify-it-py) is installed.
Either directly; `pip install linkify-it-py` or *via* `pip install myst-parser[linkify]`.
:::

(syntax/substitutions)=

## Substitutions (with Jinja2)

Adding `"substitution"` to `myst_enable_extensions` (in the sphinx `conf.py` [configuration file](https://www.sphinx-doc.org/en/master/usage/configuration.html)) will allow you to add substitutions, added in either the `conf.py` using `myst_substitutions`:

```python
myst_substitutions = {
  "key1": "I'm a **substitution**"
}
```

or at the top of the file, in the front-matter section (see [this section](syntax/frontmatter)):

````yaml
---
substitutions:
  key1: "I'm a **substitution**"
  key2: |
    ```{note}
    {{ key1 }}
    ```
  key3: <img src="img/fun-fish.png" alt="fishy" width="200px">
---
````

:::{important}
Keys in the front-matter will override ones in the `conf.py`.
:::

You can use these substitutions inline or as blocks, and you can even nest substitutions in other substitutions (but circular references are prohibited):

:::{tabbed} Markdown Input

```md
Inline: {{ key1 }}

{{ key2 }}

| col1     | col2     |
| -------- | -------- |
| {{key3}} | {{key3}} |

```

:::

:::{tabbed} Rendered Output
Inline: {{ key1 }}

{{ key2 }}

| col1     | col2     |
| -------- | -------- |
| {{key3}} | {{key3}} |

:::

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

Also, it should be noted that, inline substitutions will not parse block-level syntaxes like directives:

```
inline {{ key2 }}
```

inline {{ key2 }}

:::

Substitution references are assessed as [Jinja2 expressions](http://jinja.palletsprojects.com) which can use [filters](https://jinja.palletsprojects.com/en/2.11.x/templates/#list-of-builtin-filters), and also contains the [Sphinx Environment](https://www.sphinx-doc.org/en/master/extdev/envapi.html) in the context (as `env`).
Therefore you can do things like:

```md
{{ env.docname | upper }}
{{ "a" + "b" }}
```

{{ env.docname | upper }}
{{ "a" + "b" }}

(syntax/colon_fence)=

## Code fences using colons

By adding `"colon_fence"` to `myst_enable_extensions` (in the sphinx `conf.py` [configuration file](https://www.sphinx-doc.org/en/master/usage/configuration.html)),
you can also use `:::` delimiters to denote code fences, instead of ```` ``` ````.

Using colons instead of back-ticks has the benefit of allowing the content to be rendered correctly, when you are working in any standard Markdown editor.
It is ideal for admonition type directives (as documented in [Directives](syntax/directives)) or tables with titles, for example:

````{tabbed} Markdown Input
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

````

````{tabbed} Rendered Output

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

````

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

:::{important}
`myst_admonition_enable` is deprecated and replaced by `myst_enable_extensions = ["colon_fence"]` (see above).
Also, classes should now be set with the `:class: myclass` option.
:::

(syntax/header-anchors)=

## Auto-generated header anchors

A common, extended Markdown syntax is to use header bookmark links, locally; `[](#header-anchor)`, or cross-file `[](path/to/file.md#header-anchor)`.
To achieve this, section headings must be assigned anchors, which can be achieved in `myst-parser`,
by setting `myst_heading_anchors = 2` in your `conf.py`.
This configures heading anchors to be assigned to both `h1` and `h2` level headings.
The anchor "slugs" created aim to follow the [GitHub implementation](https://github.com/Flet/github-slugger); lower-case text, removing punctuation, replacing spaces with `-`, uniqueness *via* suffix enumeration `-1`.
You can inspect the links that will be created using the command-line tool:

```console
$ myst-anchors -l 2 docs/using/syntax-optional.md
<h1 id="optional-myst-syntaxes"></h1>
<h2 id="admonition-directives"></h2>
<h2 id="auto-generated-header-anchors"></h2>
<h2 id="definition-lists"></h2>
<h2 id="images"></h2>
<h2 id="markdown-figures"></h2>
<h2 id="direct-latex-math"></h2>
```

For example `[](#auto-generated-header-anchors)`: [](#auto-generated-header-anchors).

The paths to other files should be relative to the current file, for example
`[**link text**](./syntax.md#the-myst-syntax-guide)`: [**link text**](./syntax.md#the-myst-syntax-guide).

(syntax/definition-lists)=

## Definition Lists

By adding `"deflist"` to `myst_enable_extensions` (in the sphinx `conf.py` [configuration file](https://www.sphinx-doc.org/en/master/usage/configuration.html)),
you will be able to utilise definition lists.
Definition lists utlise the [markdown-it-py deflist plugin](markdown_it:md/plugins), which itself is based on the [Pandoc definition list specification](http://johnmacfarlane.net/pandoc/README.html#definition-lists).

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

Term 2
  ~ Definition 2a
  ~ Definition 2b

Term 3
:     A code block

: > A quote

: A final definition, that can even include images:

  <img src="img/fun-fish.png" alt="fishy" width="200px">
```

(syntax/images)=

## Images

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

By adding `"html_image"` to `myst_enable_extensions` (in the sphinx `conf.py` [configuration file](https://www.sphinx-doc.org/en/master/usage/configuration.html)),
MySt-Parser will attempt to convert any isolated `img` tags (i.e. not wrapped in any other HTML) to the internal representation used in sphinx.

```md
<img src="img/fun-fish.png" alt="fishy" class="bg-primary" width="200px">
```

<img src="img/fun-fish.png" alt="fishy" class="bg-primary mb-1" width="200px">

Allowed attributes are equivalent to the `image` directive: src, alt, class, width, height and name.
Any other attributes will be dropped.

HTML image can also be used inline!

I'm an inline image: <img src="img/fun-fish.png" height="20px">

(syntax/figures)=

## Markdown Figures

By adding `"colon_fence"` to `myst_enable_extensions` (in the sphinx `conf.py` [configuration file](https://www.sphinx-doc.org/en/master/usage/configuration.html)),
we can combine the above two extended syntaxes,
to create a fully Markdown compliant version of the `figure` directive named `figure-md`.

:::{important}
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

(syntax/amsmath)=

## Direct LaTeX Math

By adding `"amsmath"` to `myst_enable_extensions` (in the sphinx `conf.py` [configuration file](https://www.sphinx-doc.org/en/master/usage/configuration.html)),
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
