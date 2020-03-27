# Using `myst_parser` as an API

MyST-Parser may be used as an API *via* the `myst_parser` package.

```{seealso}
- The [markdown-it-py](https://github.com/ExecutableBookProject/markdown-it-py) package
- {ref}`The MyST-Parser API <api/main>`
```

The raw text is first parsed to syntax 'tokens',
then these are converted to other formats using 'renderers'.


## Quick-Start

The simplest way to understand how text will be parsed is using:

```python
from myst_parser.main import to_html
to_html("some *text*")
```

<!-- #region -->
```html
'<p>some <em>text</em></p>\n'
```
<!-- #endregion -->

```python
from myst_parser.main import to_docutils
print(to_docutils("some *text*").pformat())
```

```xml
<document source="notset">
    <paragraph>
        some
        <emphasis>
            text
```

```python
from pprint import pprint
from myst_parser.main import to_tokens

for token in to_tokens("some *text*"):
    print(token)
    print()
```

<!-- #region -->
```python
Token(type='paragraph_open', tag='p', nesting=1, attrs=None, map=[0, 1], level=0, children=None, content='', markup='', info='', meta={}, block=True, hidden=False)

Token(type='inline', tag='', nesting=0, attrs=None, map=[0, 1], level=1, children=[Token(type='text', tag='', nesting=0, attrs=None, map=None, level=0, children=None, content='some ', markup='', info='', meta={}, block=False, hidden=False), Token(type='em_open', tag='em', nesting=1, attrs=None, map=None, level=0, children=None, content='', markup='*', info='', meta={}, block=False, hidden=False), Token(type='text', tag='', nesting=0, attrs=None, map=None, level=1, children=None, content='text', markup='', info='', meta={}, block=False, hidden=False), Token(type='em_close', tag='em', nesting=-1, attrs=None, map=None, level=0, children=None, content='', markup='*', info='', meta={}, block=False, hidden=False)], content='some *text*', markup='', info='', meta={}, block=True, hidden=False)

Token(type='paragraph_close', tag='p', nesting=-1, attrs=None, map=None, level=0, children=None, content='', markup='', info='', meta={}, block=True, hidden=False)
```
<!-- #endregion -->

# The Parser


The `default_parser` function loads a standard markdown-it parser with the default syntax rules for MyST.

```python
from myst_parser.main import default_parser
parser = default_parser("html")
parser
```

<!-- #region -->
```python
markdown_it.main.MarkdownIt()
```
<!-- #endregion -->

```python
pprint(parser.get_active_rules())
```

<!-- #region -->
```python
{'block': ['front_matter',
           'table',
           'code',
           'math_block_eqno',
           'math_block',
           'fence',
           'myst_line_comment',
           'blockquote',
           'myst_block_break',
           'myst_target',
           'hr',
           'list',
           'footnote_def',
           'reference',
           'heading',
           'lheading',
           'html_block',
           'paragraph'],
 'core': ['normalize', 'block', 'inline'],
 'inline': ['text',
            'newline',
            'math_inline',
            'math_single',
            'escape',
            'myst_role',
            'backticks',
            'emphasis',
            'link',
            'image',
            'footnote_ref',
            'autolink',
            'html_inline',
            'entity'],
 'inline2': ['balance_pairs', 'emphasis', 'text_collapse']}
```
<!-- #endregion -->

```python
parser.render("*abc*")
```

<!-- #region -->
```html
'<p><em>abc</em></p>\n'
```
<!-- #endregion -->

Any of these rules can be disabled:

```python
parser.disable("emphasis").render("*abc*")
```

<!-- #region -->
```html
'<p>*abc*</p>\n'
```
<!-- #endregion -->

`renderInline` turns off any block syntax rules.

```python
parser.enable("emphasis").renderInline("- *abc*")
```

<!-- #region -->
```html
'- <em>abc</em>'
```
<!-- #endregion -->

## The Token Stream




The text is parsed to a flat token stream:

```python
from myst_parser.main import to_tokens
tokens = to_tokens("""
Here's some *text*

1. a list

> a *quote*""")
[t.type for t in tokens]
```

<!-- #region -->
```python
['paragraph_open',
 'inline',
 'paragraph_close',
 'ordered_list_open',
 'list_item_open',
 'paragraph_open',
 'inline',
 'paragraph_close',
 'list_item_close',
 'ordered_list_close',
 'blockquote_open',
 'paragraph_open',
 'inline',
 'paragraph_close',
 'blockquote_close']
```
<!-- #endregion -->

Inline type tokens contain the inline tokens as children:

```python
tokens[6]
```

<!-- #region -->
```python
Token(type='inline', tag='', nesting=0, attrs=None, map=[3, 4], level=3, children=[Token(type='text', tag='', nesting=0, attrs=None, map=None, level=0, children=None, content='a list', markup='', info='', meta={}, block=False, hidden=False)], content='a list', markup='', info='', meta={}, block=True, hidden=False)
```
<!-- #endregion -->

The sphinx renderer first converts the token to a nested structure, collapsing the opening/closing tokens into single tokens:

```python
from markdown_it.token import nest_tokens
nested = nest_tokens(tokens)
[t.type for t in nested]
```

<!-- #region -->
```python
['paragraph_open', 'ordered_list_open', 'blockquote_open']
```
<!-- #endregion -->

```python
print(nested[0].opening, end="\n\n")
print(nested[0].closing, end="\n\n")
print(nested[0].children, end="\n\n")
```

<!-- #region -->
```python
Token(type='paragraph_open', tag='p', nesting=1, attrs=None, map=[1, 2], level=0, children=None, content='', markup='', info='', meta={}, block=True, hidden=False)

Token(type='paragraph_close', tag='p', nesting=-1, attrs=None, map=None, level=0, children=None, content='', markup='', info='', meta={}, block=True, hidden=False)

[Token(type='inline', tag='', nesting=0, attrs=None, map=[1, 2], level=1, children=[Token(type='text', tag='', nesting=0, attrs=None, map=None, level=0, children=None, content="Here's some ", markup='', info='', meta={}, block=False, hidden=False), NestedTokens(opening=Token(type='em_open', tag='em', nesting=1, attrs=None, map=None, level=0, children=None, content='', markup='*', info='', meta={}, block=False, hidden=False), closing=Token(type='em_close', tag='em', nesting=-1, attrs=None, map=None, level=0, children=None, content='', markup='*', info='', meta={}, block=False, hidden=False), children=[Token(type='text', tag='', nesting=0, attrs=None, map=None, level=1, children=None, content='text', markup='', info='', meta={}, block=False, hidden=False)])], content="Here's some *text*", markup='', info='', meta={}, block=True, hidden=False)]
```
<!-- #endregion -->

## Renderers

The `myst_parser.docutils_renderer.DocutilsRenderer` converts a token directly to the `docutils.document` representation of the document, converting roles and directives to a `docutils.nodes` if a converter can be found for the given name.

```python
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
```

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
