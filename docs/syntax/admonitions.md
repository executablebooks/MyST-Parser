# Admonitions

Admonitions (also known as callouts) highlight a particular block of text,
that exists slightly apart from the narrative of your page, such as a note or a warning.

Admonitions are a special case of {{directive}} extensions.
It is advised to use admonitions with the [colon_fence](#syntax/colon_fence) extension, which signify that the content of the block is also MyST Markdown.

::::{myst-example}

:::{tip}
Let's give readers a helpful hint!
:::

::::

## Admonition types

The following core admonition types are available:

```{myst-admonitions} attention, caution, danger, error, hint, important, note, seealso, tip, warning
```

These admonitions take no argument, but may be specified with options:

:class: A space-separated list of CSS classes to add to the admonition.
:name: A reference target for the admonition (see [cross-referencing](#syntax/referencing)).

::::{myst-example}

:::{tip}
:class: myclass1,myclass2
:name: a-tip-reference
Let's give readers a helpful hint!
:::

[Reference to my tip](#a-tip-reference)

::::

Sphinx also adds a number of additional admonition types, for denoting changes to the documentation, or to the codebase:

::::{myst-example}

:::{versionadded} 1.2.3
Explanation of the new feature.
:::

:::{versionchanged} 1.2.3
Explanation of the change.
:::

:::{deprecated} 1.2.3
Explanation of the deprecation.
:::

::::

## Admonition titles

To provide a custom title for an admonition, use the `admonition` directive.
If you also want to style the admonition as one of the core admonition types,
you can use the `admonition` directive with the `class` option.

::::{myst-example}

:::{admonition} My custom title with *Markdown*!
:class: tip

This is a custom title for a tip admonition.
:::

::::

## Collapsible admonitions

The [sphinx-togglebutton](https://sphinx-togglebutton.readthedocs.io) extension allows you to create collapsible admonitions, by adding a `dropdown` class to the admonition.

::::{myst-example}

:::{note}
:class: dropdown

This admonition has been collapsed,
meaning you can add longer form content here,
without it taking up too much space on the page.
:::

::::

## Other Containers (grids, tabs, cards, etc.)

Using the [colon_fence](#syntax/colon_fence) extension,
content block can be wrapped in containers with a custom CSS class.

::::{myst-example}
:::bg-primary
This is a container with a custom CSS class.

- It can contain multiple blocks
:::
::::

Using the [sphinx-design](https://github.com/executablebooks/sphinx-design) extension,
it is also possible to create beautiful, screen-size responsive web-components.

::::{myst-example}
:::{card} Card Title
Header
^^^
Card content
+++
Footer
:::
::::


::::::{myst-example}

::::{tab-set}

:::{tab-item} Label1
Content 1
:::

:::{tab-item} Label2
Content 2
:::

::::

::::::
