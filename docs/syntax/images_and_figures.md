# Images and figures

MyST Markdown can be used to include images and figures in your documents as well as referencing those images easily throughout your project.

## Inline images

The standard Markdown syntax for images is:

:::{myst-example}
![fishy](img/fun-fish.png)
:::

This will create an **inline** image, which is displayed in the flow of the text.

The [attrs_inline](syntax/attributes/inline) extension can be used to add attributes to an inline image:

:::{myst-example}
![fishy](img/fun-fish.png){.bg-warning w=100px align=center}
:::

The [html_image](syntax/images/html) extension can also be used, to allow MyST to parse HTML image tags:

:::{myst-example}
:highlight: html

<img src="img/fun-fish.png" alt="fishy" width="200px" class="bg-primary">
:::

## Block level images

To create a **block** image, use the `image` directive:

:::{myst-example}
```{image} img/fun-fish.png
:alt: fishy
:class: bg-primary
:width: 200px
:align: center
```
:::

The following options are recognized:

:::{admonition} Image options
:class: hint

``alt`` : text
: Alternate text: a short description of the image, displayed by
  applications that cannot display images, or spoken by applications
  for visually impaired users.

``height`` : [length](units/length)
: The desired height of the image.
  Used to reserve space or scale the image vertically.
  When the "scale" option is also specified, they are combined.
  For example, a height of 200px and a scale of 50 is equivalent to a height of 100px with no scale.

``width`` : [length](units/length) or [percentage](units/percentage) of the current line width
: The width of the image.
  Used to reserve space or scale the image horizontally.  As with "height"
  above, when the "scale" option is also specified, they are combined.

``scale`` : integer percentage (the "%" symbol is optional)
: The uniform scaling factor of the image.  The default is "100 %", i.e.
  no scaling.

``align`` : "top", "middle", "bottom", "left", "center", or "right"
: The values "top", "middle", and "bottom" control an image's vertical alignment
: The values "left", "center", and "right" control an image's horizontal alignment,
  allowing the image to float and have the text flow around it.

``target`` : text (URI or reference name)
: Makes the image into a hyperlink reference ("clickable").

``class``
: A space-separated list of CSS classes to add to the image.

``name``
: A reference target for the admonition (see [cross-referencing](#syntax/referencing)).

:::

## Figures (images with captions)

To create a **figure**, use the `figure` directive:

:::{myst-example}
```{figure} img/fun-fish.png
:scale: 50 %
:alt: map to buried treasure

This is the caption of the figure (a simple paragraph).

The legend consists of all elements after the caption.  In this
case, the legend consists of this paragraph and the following
table:

| Symbol | Meaning |
| ------ | ------- |
| :fish: | fishy   |

```
:::

The "figure" directive supports all of the options of the "image" directive, as well as the following:

:::{admonition} Figure options
:class: hint

figwidth : "image", [length](units/length) or [percentage](units/percentage) of current line width
: The width of the figure.  If the value is "image", the width of the
  image is used.  Otherwise, the value is interpreted as a length or
  percentage of the current line width.

figclass : text
: A space-separated list of CSS classes to add to the figure (`class` are added to the image).

:::

:::::{seealso}

See the <project:#syntax/md-figures> section for information on how to create figures that use native Markdown images.

::::{myst-example}
:::{figure-md}
![fishy](img/fun-fish.png){width=200px}

This is a caption in __*Markdown*__
:::
::::

:::::

## Figures with multiple images

See the [sphinx-subfigure](https://sphinx-subfigure.readthedocs.io) extension for a way to create figures with multiple images.

% TODO this can uncommented once https://github.com/mgaitan/sphinxcontrib-mermaid/issues/109 is fixed
% ## Diagrams

% It is possible to use [mermaid diagrams](https://mermaid-js.github.io/mermaid) using the `sphinxcontrib.mermaid` extension.

% :::{myst-example}
% ```{mermaid}
% flowchart LR
%   A[Jupyter Notebook] --> C
%   B[MyST Markdown] --> C
%   C(mystjs) --> D{AST}
%   D <--> E[LaTeX]
%   E --> F[PDF]
%   D --> G[Word]
%   D --> H[React]
%   D --> I[HTML]
%   D <--> J[JATS]
% ```
% :::
