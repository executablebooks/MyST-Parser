(syntax-optional)=

# Optional MyST Syntaxes

MyST-Parser is highly configurable, utilising the inherent "plugability" of the [markdown-it-py](markdown_it:index) parser.
The following syntaxes are optional (disabled by default) and can be enabled *via* the sphinx `conf.py` (see [](intro/config-options)).
Their goal is generally to add more *Markdown friendly* syntaxes; often enabling and rendering [markdown-it-py plugins](markdown_it:md/plugins) that extend the [CommonMark specification](https://commonmark.org/).

(syntax/admonitions)=

## Admonition directives

A special syntax for admonitions can optionally be enabled by setting `myst_admonition_enable = True` in the sphinx `conf.py` [configuration file](https://www.sphinx-doc.org/en/master/usage/configuration.html).

The key differences are that, instead of back-ticks, colons are used, and **the content starts as regular Markdown**.
This has the benefit of allowing the content to be rendered correctly, when you are working in any standard Markdown editor.
For example:

```md
:::{note}
This text is **standard** _Markdown_
:::
```

:::{note}
This text is **standard** _Markdown_
:::

Similar to normal directives, these admonitions can also be nested:

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

The supported directives are: admonition, attention, caution, danger, error, important, hint, note, seealso, tip and warning.

These directives do **not** currently allow for parameters to be set, but you can add additional CSS classes to the admonition as comma-delimited arguments after the directive name. Also `admonition` can have a custom title.
For example:

```md
:::{admonition,warning} This *is* also **Markdown**
This text is **standard** _Markdown_
:::
```

:::{admonition,warning} This *is* also **Markdown**
This text is **standard** _Markdown_
:::

(syntax/definition-lists)=

## Definition Lists

By setting `myst_deflist_enable = True` in the sphinx `conf.py` configuration file, you will be able to utilise definition lists.
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
By setting `myst_html_img_enable = True` in the sphinx `conf.py` configuration file, MySt-Parser will attempt to convert any isolated `img` tags (i.e. not wrapped in any other HTML) to the internal representation used in sphinx.

```md
<img src="img/fun-fish.png" alt="fishy" class="bg-primary" width="200px">
```

<img src="img/fun-fish.png" alt="fishy" class="bg-primary mb-1" width="200px">

Allowed attributes are equivalent to the `image` directive: src, alt, class, width, height and name.
Any other attributes will be dropped.

(syntax/figures)=

## Markdown Figures

Setting `myst_figure_enable = True` in your sphinx `conf.py`, combines the above two extended syntaxes,
to create a fully Markdown compliant version of the `figure` directive.

The figure block must contain **only** two components; an image, in either Markdown or HTML syntax, and a single paragraph for the caption.

As with admonitions, the figure can have additional classes set on it, but the title is now taken as the reference target of the figure:

```md
:::{figure,myclass} fig-target
<img src="img/fun-fish.png" alt="fishy" class="bg-primary mb-1" width="200px">

This is a caption in **Markdown**
:::
```

:::{figure,myclass} fig-target
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

You can enable direct parsing of [amsmath](https://ctan.org/pkg/amsmath) LaTeX equations by setting `myst_amsmath_enable = True` in your sphinx `conf.py`.
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
