# Parse MyST Markdown

```{seealso}
- The MyST Parser package heavily uses the the [markdown-it-py](https://github.com/executablebooks/markdown-it-py) package.
- {ref}`The MyST-Parser API reference <api/main>` contains a more complete reference of this API.
```

## Parsing and rendering helper functions

The MyST Parser comes bundled with some helper functions to quickly parse MyST Markdown and render its output.

:::{important}
These APIs are primarily intended for testing and development purposes.
For proper parsing see {ref}`myst-sphinx` and {ref}`myst-docutils`.
:::

### Parse MyST Markdown to HTML

The following code parses markdown and renders as HTML using only the markdown-it parser
(i.e. no sphinx or docutils specific processing is done):

```python
from myst_parser.main import to_html
to_html("some *text* {literal}`a`")
```

<!-- #region -->
```html
'<p>some <em>text</em> <code class="myst role">{literal}[a]</code></p>\n'
```
<!-- #endregion -->

### Parse MyST Markdown to docutils

The following function renders your text as **docutils AST objects** (for example, for use with the Sphinx ecosystem):

```python
from myst_parser.main import to_docutils
print(to_docutils("some *text* {literal}`a`").pformat())
```

```xml
<document source="notset">
    <paragraph>
        some
        <emphasis>
            text

        <literal>
            a
```

:::{note}
This function only performs the initial parse of the AST,
without applying any transforms or post-processing.
See for example the [Sphinx core events](https://www.sphinx-doc.org/en/master/extdev/appapi.html?highlight=config-inited#sphinx-core-events).
:::

### Parse MyST Markdown as `markdown-it` tokens

The MyST Parser uses `markdown-it-py` tokens as an intermediate representation of your text.
Normally these tokens are then *rendered* into various outputs.
If you'd like direct access to the tokens, use the `to_tokens` function.
Here's an example of its use:

```python
from pprint import pprint
from myst_parser.main import to_tokens

for token in to_tokens("some *text*"):
    print(token, "\n")
```

<!-- #region -->
```python
Token(type='paragraph_open', tag='p', nesting=1, attrs=None, map=[0, 1], level=0, children=None, content='', markup='', info='', meta={}, block=True, hidden=False)

Token(type='inline', tag='', nesting=0, attrs=None, map=[0, 1], level=1, children=[Token(type='text', tag='', nesting=0, attrs=None, map=None, level=0, children=None, content='some ', markup='', info='', meta={}, block=False, hidden=False), Token(type='em_open', tag='em', nesting=1, attrs=None, map=None, level=0, children=None, content='', markup='*', info='', meta={}, block=False, hidden=False), Token(type='text', tag='', nesting=0, attrs=None, map=None, level=1, children=None, content='text', markup='', info='', meta={}, block=False, hidden=False), Token(type='em_close', tag='em', nesting=-1, attrs=None, map=None, level=0, children=None, content='', markup='*', info='', meta={}, block=False, hidden=False)], content='some *text*', markup='', info='', meta={}, block=True, hidden=False)

Token(type='paragraph_close', tag='p', nesting=-1, attrs=None, map=None, level=0, children=None, content='', markup='', info='', meta={}, block=True, hidden=False)
```
<!-- #endregion -->

Each token is an abstract representation of a piece of MyST Markdown syntax.

## Use the parser object for more control

The MyST Parser is actually a `markdown-it-py` parser with several extensions pre-enabled that support the MyST syntax.
If you'd like more control over the parsing process, then you can directly use a `markdown-it-py` parser with MyST syntax extensions loaded.

:::{seealso}
[`markdown-it-py`](https://markdown-it-py.readthedocs.io/) is an extensible Python parser and renderer for flavors of markdown.
It is inspired heavily by the [`markdown-it`](https://github.com/markdown-it/markdown-it) Javascript package.
See the documentation of these tools for more information.
:::

### Load a parser

To load one of these parsers for your own use, use the `default_parser` function.
Below we'll create such a parser and show that it is an instance of a `markdown-it-py` parser:

```python
from myst_parser.main import default_parser, MdParserConfig
config = MdParserConfig(renderer="html")
parser = default_parser(config)
parser
```

<!-- #region -->
```python
markdown_it.main.MarkdownIt()
```
<!-- #endregion -->

### List the active rules

We can list the **currently active rules** for this parser.
Each rules maps onto a particular markdown syntax, and a Token.
To list the active rules, use the `get_active_rules` method:

```python
pprint(parser.get_active_rules())
```

<!-- #region -->
```python
{'block': ['front_matter',
           'table',
           'code',
           'math_block_label',
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

### Parse and render markdown

Once we have a Parser instance, we can use it to parse some markdown.
Use the `render` function to do so:

```python
parser.render("*abc*")
```

<!-- #region -->
```html
'<p><em>abc</em></p>\n'
```
<!-- #endregion -->

### Disable and enable rules

You can disable and enable rules for a parser using the `disable` and `enable` methods.
For example, below we'll disable the `emphasis` rule (which is what detected the `*abc*` syntax above) and re-render the text:

```python
parser.disable("emphasis").render("*abc*")
```

<!-- #region -->
```html
'<p>*abc*</p>\n'
```
<!-- #endregion -->

As you can see, the parser no longer detected the `*<text>*` syntax as requiring an _emphasis_.

### Turn off all block-level syntax

If you'd like to use your parser *only* for in-line content, you may turn off all block-level syntax with the `renderInline` method:

```python
parser.enable("emphasis").renderInline("- *abc*")
```

<!-- #region -->
```html
'- <em>abc</em>'
```
<!-- #endregion -->


## The Token Stream

When you parse markdown with the MyST Parser, the result is a flat stream of **Tokens**.
These are abstract representations of each type of syntax that the parser has detected.

For example, below we'll show the token stream for some simple markdown:

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

Note that these tokens are **flat**, although some of the tokens refere to one another (for example, Tokens with `_open` and `_close` represent the start/end of blocks).

Tokens of type `inline` will have a `children` attribute that contains a list of the Tokens that they contain.
For example:

```python
tokens[6]
```

<!-- #region -->
```python
Token(type='inline', tag='', nesting=0, attrs=None, map=[3, 4], level=3, children=[Token(type='text', tag='', nesting=0, attrs=None, map=None, level=0, children=None, content='a list', markup='', info='', meta={}, block=False, hidden=False)], content='a list', markup='', info='', meta={}, block=True, hidden=False)
```
<!-- #endregion -->

### Rendering tokens

The list of Token objects can be rendered to a number of different outputs.
This involves first processing the Tokens, and then defining how each should be rendered in an output format (e.g., HTML or Docutils).

For example, the sphinx renderer first converts the token to a nested structure, collapsing the opening/closing tokens into single tokens:

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

It then renders each token to a Sphinx-based docutils object.
See [the renderers section](renderers.md) for more information about rendering tokens.
