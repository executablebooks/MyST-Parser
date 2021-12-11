# Render outputs

```{autoclass} myst_parser.docutils_renderer.DocutilsRenderer
:special-members: __output__, __init__
:members: render, nested_render_text, add_line_and_source_path, current_node_context
:undoc-members:
:member-order: bysource
:show-inheritance:
```

There are a few different ways to render MyST Parser tokens into different outputs.
This section covers a few common ones.

## The `docutils` renderer

The `myst_parser.docutils_renderer.DocutilsRenderer` converts a token directly to the `docutils.document` representation of the document, converting roles and directives to a `docutils.nodes` if a converter can be found for the given name.

````python
from myst_parser.main import to_docutils

document = to_docutils("""
Here's some *text*

1. a list

> a quote

{emphasis}`content`

```{sidebar} my sidebar
content
```
""")

print(document.pformat())
````

```xml
<document source="notset">
    <paragraph>
        Here's some
        <emphasis>
            text
    <enumerated_list>
        <list_item>
            <paragraph>
                a list
    <block_quote>
        <paragraph>
            a quote
    <paragraph>
        <emphasis>
            content
    <sidebar>
        <title>
            my sidebar
        <paragraph>
            content
```

## The Sphinx renderer

The `myst_parser.sphinx_renderer.SphinxRenderer` builds on the `DocutilsRenderer` to add sphinx specific nodes, e.g. for cross-referencing between documents.

To use the sphinx specific roles and directives outside of a `sphinx-build`, they must first be loaded with the `in_sphinx_env` option.

````python
document = to_docutils("""
Here's some *text*

1. a list

> a quote

{ref}`target`

```{glossary} my gloassary
name
    definition
```
""",
    in_sphinx_env=True)
print(document.pformat())
````

```xml
<document source="notset">
    <paragraph>
        Here's some
        <emphasis>
            text
    <enumerated_list>
        <list_item>
            <paragraph>
                a list
    <block_quote>
        <paragraph>
            a quote
    <paragraph>
        <pending_xref refdoc="mock_docname" refdomain="std" refexplicit="False" reftarget="target" reftype="ref" refwarn="True">
            <inline classes="xref std std-ref">
                target
    <glossary>
        <definition_list classes="glossary">
            <definition_list_item>
                <term ids="term-my-gloassary">
                    my gloassary
                    <index entries="('single',\ 'my\ gloassary',\ 'term-my-gloassary',\ 'main',\ None)">
                <term ids="term-name">
                    name
                    <index entries="('single',\ 'name',\ 'term-name',\ 'main',\ None)">
                <definition>
                    <paragraph>
                        definition
```

### Set Sphinx configuration for testing

You can also set Sphinx configuration *via* `sphinx_conf`. This is a dictionary representation of the contents of the Sphinx `conf.py`.

```{warning}
This feature is only meant for simple testing.
It will fail for extensions that require the full
Sphinx build process and/or access to external files.
```

`````python
document = to_docutils("""
````{tabs}

```{tab} Apples

Apples are green, or sometimes red.
```
````
""",
    in_sphinx_env=True,
    conf={"extensions": ["sphinx_tabs.tabs"]}
)
print(document.pformat())
`````

```xml
<document source="notset">
    <container classes="sphinx-tabs">
        <container>
            <a classes="item">
                <container>
                    <paragraph>
                        Apples
            <container classes="ui bottom attached sphinx-tab tab segment sphinx-data-tab-0-0 active">
                <paragraph>
                    Apples are green, or sometimes red.
```
