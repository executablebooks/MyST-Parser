# Using `myst_parser` as an API

% TODO eventually this should be wrote as a notebook (with MyST-NB)!

MyST-Parser may be used as an API *via* the `myst_parser` package.
The raw text is first parsed to syntax 'tokens',
then these are converted to other formats using 'renderers'.

The simplest way to parse text is using:

```python
from myst_parser import parse_text
parse_text("some *text*", "html")
```

```html
'<p>some <em>text</em></p>\n'
```

The output type can be one of:

- `dict` (a.k.a ast)
- `html`
- `docutils`
- `sphinx`

## Convert Text to Tokens

To convert some text to tokens:

```python
from myst_parser import text_to_tokens
root = text_to_tokens("""
Here's some *text*

1. a list

> a *quote*""")
root
```

```python
MyST.Document(blocks=3)
```

All non-terminal tokens may contain children:

```python
root.children
```

```python
[MyST.Paragraph(range=(2, 2),children=2),
 MyST.List(items=1),
 MyST.Quote(range=(6, 6),children=1)]
```

Then each token has attributes specific to its type:

```python
list_token = root.children[1]
list_token.__dict__
```

```python
{'children': [MyST.ListItem(children=1)], 'loose': False, 'start': 1}
```

You can also recursively traverse the syntax tree, yielding `TraverseResult`s that contain the element, its parent and depth from the source token:

```python
from pprint import pprint
from myst_parser import traverse
tree = [
    (t.parent.__class__.__name__, t.node.__class__.__name__, t.depth)
    for t in traverse(root)
]
pprint(tree)
```

```python
[('Document', 'Paragraph', 1),
 ('Document', 'List', 1),
 ('Document', 'Quote', 1),
 ('Paragraph', 'RawText', 2),
 ('Paragraph', 'Emphasis', 2),
 ('List', 'ListItem', 2),
 ('Quote', 'Paragraph', 2),
 ('Emphasis', 'RawText', 3),
 ('ListItem', 'Paragraph', 3),
 ('Paragraph', 'RawText', 3),
 ('Paragraph', 'Emphasis', 3),
 ('Paragraph', 'RawText', 4),
 ('Emphasis', 'RawText', 4)]
```

## AST Renderer

The `myst_parser.ast_renderer.AstRenderer` converts a token to a nested dictionary representation.

```python
from pprint import pprint
from myst_parser import render_tokens
from myst_parser.ast_renderer import AstRenderer

pprint(render_tokens(root, AstRenderer))
```

```python
{'children': [{'children': [{'content': "Here's some ", 'type': 'RawText'},
                            {'children': [{'content': 'text',
                                           'type': 'RawText'}],
                             'type': 'Emphasis'}],
               'range': (2, 2),
               'type': 'Paragraph'},
              {'children': [{'children': [{'children': [{'content': 'a list',
                                                         'type': 'RawText'}],
                                           'range': (1, 1),
                                           'type': 'Paragraph'}],
                             'leader': '1.',
                             'loose': False,
                             'prepend': 3,
                             'type': 'ListItem'}],
               'loose': False,
               'start': 1,
               'type': 'List'},
              {'children': [{'children': [{'content': 'a quote',
                                           'type': 'RawText'}],
                             'range': (7, 7),
                             'type': 'Paragraph'}],
               'range': (6, 6),
               'type': 'Quote'}],
 'footnotes': {},
 'type': 'Document'}
```

## HTML Renderer

The `myst_parser.html_renderer.HTMLRenderer` converts a token directly to HTML.

```python
from myst_parser import render_tokens
from myst_parser.html_renderer import HTMLRenderer

print(render_tokens(root, HTMLRenderer))
```

```html
<p>Here's some <em>text</em></p>
<ol>
<li>a list</li>
</ol>
<blockquote>
<p>a <em>quote</em></p>
</blockquote>
```

`````{note}
This render will not actually 'assess' roles and directives,
just represent their raw content:

````python
other = text_to_tokens("""
{role:name}`content`

```{directive_name} arg
:option: a
content
```
""")

print(render_tokens(other, HTMLRenderer))
````

````html
<p><span class="myst-role"><code>{role:name}content</code></span></p>
<div class="myst-directive">
<pre><code>{directive_name} arg
:option: a
content
</code></pre></span>
</div>
````
`````

You can also create a minmal page preview, including CSS:

```python
parse_text(
    in_string,
    "html",
    add_mathjax=True,
    as_standalone=True,
    add_css=dedent(
        """\
        div.myst-front-matter {
            border: 1px solid gray;
        }
        div.myst-directive {
            background: lightgreen;
        }
        hr.myst-block-break {
            border-top:1px dotted black;
        }
        span.myst-role {
            background: lightgreen;
        }
        """
    ),
)
```

## Docutils Renderer

The `myst_parser.docutils_renderer.DocutilsRenderer` converts a token directly to the `docutils.document` representation of the document, converting roles and directives to a `docutils.nodes` if a converter can be found for the given name.

````python
from myst_parser import render_tokens
from myst_parser.docutils_renderer import DocutilsRenderer

root = text_to_tokens("""
Here's some *text*

1. a list

> a quote

{emphasis}`content`

```{sidebar} my sidebar
content
```
""")

document = render_tokens(root, DocutilsRenderer)
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

## Sphinx Renderer

The `myst_parser.docutils_renderer.SphinxRenderer` builds on the `DocutilsRenderer` to add sphinx specific nodes, e.g. for cross-referencing between documents.

```{note}
To use sphinx specific roles and directives outside of a `sphinx-build`, they must first be loaded with the `load_sphinx_env=True` option.
```

````python
from myst_parser import text_to_tokens, render_tokens
from myst_parser.docutils_renderer import SphinxRenderer

root = text_to_tokens("""
Here's some *text*

1. a list

> a quote

{ref}`target`

```{glossary} my gloassary
name
    definition
```
""")

document = render_tokens(root, SphinxRenderer, load_sphinx_env=True)
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

You can also set Sphinx configuration *via* `sphinx_conf`. This is a dictionary representation of the contents of the Sphinx `conf.py`.

```{warning}
This feature is only meant for simple testing.
It will fail for extensions that require the full
Sphinx build process and/or access to external files.
```

`````python
from myst_parser import text_to_tokens, render_tokens
from myst_parser.docutils_renderer import SphinxRenderer

root = text_to_tokens("""
````{tabs}

```{tab} Apples

Apples are green, or sometimes red.
```
````
""")

document = render_tokens(root, SphinxRenderer, load_sphinx_env=True, sphinx_conf={"extensions": ["sphinx_tabs.tabs"]})
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
