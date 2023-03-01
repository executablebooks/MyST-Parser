(syntax/code-blocks)=
# Source code and APIs

## Basic block syntax highlighting

Code blocks contain a language identifier, which is used to determine the language of the code.
This language is used to determine the syntax highlighting, using an available [pygments lexer](https://pygments.org/docs/lexers/).

:::{myst-example}
```python
from a import b
c = "string"
```
:::

::::{admonition} Adding a language lexer
:class: tip dropdown
You can create and register your own lexer, using the [`pygments.lexers` entry point](https://pygments.org/docs/plugins/#register-plugins),
or within a sphinx extension, with the [`app.add_lexer` method](inv:sphinx#*.Sphinx.add_lexer).
::::

::::{admonition} Show backticks inside raw markdown blocks
:class: tip dropdown

If you'd like to show backticks inside of your markdown,
you can do so by nesting them in backticks of a greater length.
Markdown will treat the outer-most backticks as the edges of the "raw" block and everything inside will show up.
For example:

:::{myst-example}
`` `hi` ``

````
```
hi
```
````
:::

::::

## Inline syntax highlighting

The [attrs_inline](#syntax/attributes/inline) extension can be used to apply syntax highlighting to inline code:

:::{myst-example}
Inline Python code `a = "b"`{l=python}
:::

## Numbering and highlighting lines

To set a global default for line numbering, per lexer name,
the `myst_number_code_blocks` [configuration option](#sphinx/config-options) can be used.
For example, using:

```python
myst_number_code_blocks = ["typescript"]
```

Will number all code blocks with the `typescript` lexer by default.

:::{myst-example}
```typescript
type MyBool = true | false;

interface User {
  name: string;
  id: number;
}
```
:::

To apply numbering and highlighting to a specific code block,
the [attrs_block](#syntax/attributes/block) extension can be used:

:::{myst-example}
{lineno-start=1 emphasize-lines="2,3"}
```python
a = 1
b = 2
c = 3
```
:::

## Adding a caption

With the `code-block` {{directive}},
a caption can be added to a code blocks, as well as other options:

:::{myst-example}
```{code-block} python
:caption: This is a caption
:emphasize-lines: 2,3
:lineno-start: 1

a = 1
b = 2
c = 3
```
:::

The following options are recognized:

:::{admonition} Code block options
:class: hint dropdown

`linenos` : flag
: Enable to generate line numbers for the code block

`lineno-start` : integer
: The starting line number for the code block (`linenos` is automatically enabled)

`emphasize-lines` : comma-separated list of integers
: Highlight the specified lines

`caption` : string
: The caption for the code block

`force` : flag
: Allow minor errors on highlighting to be ignored

`name` : string
: The name of the code block, which can be referenced elsewhere in the document

`class` : string
: The class to apply to the code block

```{seealso}
The [Sphinx documentation](inv:sphinx#code-block)
```

:::

(syntax/literalinclude)=
## Including code from files

Longer pieces of code can be included from files using the `literalinclude` {{directive}}:

:::{myst-example}
```{literalinclude} examples/example.py
```
:::

The file name is usually relative to the current file’s path. However, if it is absolute (starting with `/`), it is relative to the top source directory.

To select only a sub-section of the file, the `lines`, `pyobject` or `start-after` and `end-before` options can be used:

:::{myst-example}
```{literalinclude} examples/example.py
:start-after: start example
:end-before: end example
```
:::

```{seealso}
The [Sphinx documentation](inv:sphinx#literalinclude)
```

(syntax/apis)=
## Documenting whole APIs

Sphinx and MyST provide means to analyse source code and automatically generate documentation and referenceable links for APIs.

`sphinx.ext.autodoc` can be used ([see below](#syntax/apis/sphinx-autodoc)), however, it is not inherently compatible with MyST Markdown, and so the `sphinx-autodoc2` extension is recommended.

(syntax/apis/sphinx-autodoc2)=
### `sphinx-autodoc2`

[`sphinx-autodoc2`](https://sphinx-autodoc2.readthedocs.io) is an extension for Sphinx that provides an integrated means to document Python APIs.

As opposed to `sphinx.ext.autodoc`, `sphinx-autodoc2` performs static (rather than dynamic) analysis of the source code, integrates full package documenting, and also allows for docstrings to be written in both RestructureText and MyST.

The `auto_mode` will automatically generate the full API documentation, as shown <project:/apidocs/index.rst>.

Alternatively, the `autodoc2-object` directive can be used to generate documentation for a single object.
To embed in a MyST document the MyST `render_plugin` should be specified, for example:

````{myst-example}
```{autodoc2-object} myst_parser.sphinx_ext.main.setup_sphinx
render_plugin = "myst"
no_index = true
```
````

This can be referenced elsewhere in the document using the `:py:obj:` role, or a `#` link (see [cross-referencing](#syntax/referencing)).

````{myst-example}
- {py:obj}`myst_parser.sphinx_ext.main.setup_sphinx`
- [](#myst_parser.sphinx_ext.main.setup_sphinx)
````

Additionally, summaries of multiple objects can be generated using the `autodoc2-summary` directive:

````{myst-example}
```{autodoc2-summary}
:renderer: myst

~myst_parser.sphinx_ext.main.setup_sphinx
~myst_parser.sphinx_ext.main.create_myst_config
```
````

#### Using MyST docstrings

`sphinx-autodoc2` can be configured to use MyST docstrings (rather than RestructureText), for the entire project or select objects, by setting the `autodoc2_docstring_parser_regexes` configuration option:

```python
autodoc2_docstring_parser_regexes = [
    # this will render all docstrings as Markdown
    (r".*", "myst"),
    # this will render select docstrings as Markdown
    (r"mypackage\.mymodule\..*", "myst"),
]
```

For example:

````{myst-example}
```{autodoc2-object} myst_parser.setup
render_plugin = "myst"
no_index = true
docstring_parser_regexes = [
    ["myst_parser\\.setup", "myst"],
]
```
````

(syntax/apis/sphinx-autodoc)=
### `sphinx.ext.autodoc`

[Sphinx extension `autodoc`](inv:sphinx#sphinx.ext.autodoc) also can generate documentation for Python objects.
However, because it is hard-coded to generate RestructureText, the special [`eval-rst` directive](#syntax/directives/parsing) needs to be used:

````{myst-example}
```{eval-rst}
.. autofunction:: myst_parser.sphinx_ext.main.setup_sphinx
    :noindex:
```
````

Summaries can also be generated with [`autosummary`](inv:sphinx#sphinx.ext.autosummary):

````{myst-example}
```{eval-rst}
.. autosummary::
    :nosignatures:

    myst_parser.sphinx_ext.main.setup_sphinx
    myst_parser.sphinx_ext.main.create_myst_config
```
````
