(roles-directives)=

# Roles and Directives

Roles and directives provide a way to extend the syntax of MyST in an unbound manner,
by interpreting a chuck of text as a specific type of markup, according to its name.

Mostly all
[docutils roles](https://docutils.sourceforge.io/docs/ref/rst/roles.html),
[docutils directives](https://docutils.sourceforge.io/docs/ref/rst/directives.html),
[Sphinx roles](inv:sphinx#usage/*/roles), or
[Sphinx directives](inv:sphinx#usage/*/directives)
can be used in MyST.

## Syntax

(syntax/directives)=

### Directives - a block-level extension point

Directives syntax is defined with triple-backticks and curly-brackets.
It is effectively a Markdown code fence with curly brackets around the language, and a directive name in place of a language name.
Here is the basic structure:

`````{list-table}
---
header-rows: 1
---
* - MyST
  - reStructuredText
* - ````md
    ```{directivename} arguments
    ---
    key1: val1
    key2: val2
    ---
    This is
    directive content
    ```
    ````
  - ```rst
    .. directivename:: arguments
       :key1: val1
       :key2: val2

       This is
       directive content
    ```
`````

For example, the following code:

````md
```{admonition} This is my admonition
This is my note
```
````

Will generate this admonition:

```{admonition} This is my admonition
This is my note
```

#### Parameterizing directives

For directives that take parameters as input, there are two ways to parameterize them.
In each case, the options themselves are given as `key: value` pairs. An example of
each is shown below:

**Using YAML frontmatter**. A block of YAML front-matter just after the
first line of the directive will be parsed as options for the directive. This needs to be
surrounded by `---` lines. Everything in between will be parsed by YAML and
passed as keyword arguments to your directive. For example:

````md
```{code-block} python
---
lineno-start: 10
emphasize-lines: 1, 3
caption: |
    This is my
    multi-line caption. It is *pretty nifty* ;-)
---
a = 2
print('my 1st line')
print(f'my {a}nd line')
```
````

```{code-block} python
---
lineno-start: 10
emphasize-lines: 1, 3
caption: |
    This is my
    multi-line caption. It is *pretty nifty* ;-)
---
a = 2
print('my 1st line')
print(f'my {a}nd line')
```

**Short-hand options with `:` characters**. If you only need one or two options for your
directive and wish to save lines, you may also specify directive options as a collection
of lines just after the first line of the directive, each preceding with `:`. Then the
leading `:` is removed from each line, and the rest is parsed as YAML.

For example:

````md
```{code-block} python
:lineno-start: 10
:emphasize-lines: 1, 3

a = 2
print('my 1st line')
print(f'my {a}nd line')
```
````

(syntax/directives/parsing)=

#### How directives parse content

Some directives parse the content that is in their content block.
MyST parses this content **as Markdown**.

This means that MyST markdown can be written in the content areas of any directives written in MyST markdown. For example:

````md
```{admonition} My markdown link
Here is [markdown link syntax](https://jupyter.org)
```
````

```{admonition} My markdown link
Here is [markdown link syntax](https://jupyter.org)
```

As a short-hand for directives that require no arguments, and when no parameter options are used (see below),
you may start the content directly after the directive name.

````md
```{note} Notes require **no** arguments, so content can start here.
```
````

```{note} Notes require **no** arguments, so content can start here.
```

For special cases, MySt also offers the `eval-rst` directive.
This will parse the content **as ReStructuredText**:

````md
```{eval-rst}
.. figure:: img/fun-fish.png
  :width: 100px
  :name: rst-fun-fish

  Party time!

A reference from inside: :ref:`rst-fun-fish`

A reference from outside: :ref:`syntax/directives/parsing`
```
````

```{eval-rst}
.. figure:: img/fun-fish.png
  :width: 100px
  :name: rst-fun-fish

  Party time!

A reference from inside: :ref:`rst-fun-fish`

A reference from outside: :ref:`syntax/directives/parsing`
```

Note how the text is integrated into the rest of the document, so we can also reference [party fish](rst-fun-fish) anywhere else in the documentation.

#### Nesting directives

You can nest directives by ensuring that the tick-lines corresponding to the
outermost directive are longer than the tick-lines for the inner directives.
For example, nest a warning inside a note block like so:

`````md
````{note}
The next info should be nested
```{warning}
Here's my warning
```
````
`````

Here's how it looks rendered:

````{note}
The next info should be nested
```{warning}
Here's my warning
```
````

You can indent inner-code fences, so long as they aren't indented by more than 3 spaces.
Otherwise, they will be rendered as "raw code" blocks:

`````md
````{note}
The warning block will be properly-parsed

   ```{warning}
   Here's my warning
   ```

But the next block will be parsed as raw text

    ```{warning}
    Here's my raw text warning that isn't parsed...
    ```
````
`````

````{note}
The warning block will be properly-parsed

   ```{warning}
   Here's my warning
   ```

But the next block will be parsed as raw text

    ```{warning}
    Here's my raw text warning that isn't parsed...
    ```
````

This can really be abused if you'd like ;-)

``````{note}
The next info should be nested
`````{warning}
Here's my warning
````{admonition} Yep another admonition
```python
# All this fuss was about this boring python?!
print('yep!')
```
````
`````
``````

#### Markdown-friendly directives

Want to use syntax that renders correctly in standard Markdown editors?
See [the extended syntax option](syntax/colon_fence).

```md
:::{note}
This text is **standard** *Markdown*
:::
```

:::{note}
This text is **standard** *Markdown*
:::

(syntax/roles)=

### Roles - an in-line extension point

Roles are similar to directives - they allow you to define arbitrary new functionality, but they are used *in-line*.
To define an in-line role, use the following form:

````{list-table}
---
header-rows: 1
---
* - MyST
  - reStructuredText
* - ````md
    {role-name}`role content`
    ````
  - ```rst
    :role-name:`role content`
    ```
````

For example, the following code:

```md
Since Pythagoras, we know that {math}`a^2 + b^2 = c^2`
```

Becomes:

Since Pythagoras, we know that {math}`a^2 + b^2 = c^2`

You can use roles to do things like reference equations and other items in
your book. For example:

````md
```{math} e^{i\pi} + 1 = 0
---
label: euler
---
```

Euler's identity, equation {math:numref}`euler`, was elected one of the
most beautiful mathematical formulas.
````

Becomes:

```{math} e^{i\pi} + 1 = 0
---
label: euler
---
```

Euler's identity, equation {math:numref}`euler`, was elected one of the
most beautiful mathematical formulas.

#### How roles parse content

The content of roles is parsed differently depending on the role that you've used.
Some roles expect inputs that will be used to change functionality. For example,
the `ref` role will assume that input content is a reference to some other part of the
site. However, other roles may use the MyST parser to parse the input as content.

Some roles also **extend their functionality** depending on the content that you pass.
For example, following the `ref` example above, if you pass a string like this:
`Content to display <myref>`, then the `ref` will display `Content to display` and use
`myref` as the reference to look up.

How roles parse this content depends on the author that created the role.

## Common roles and directives

:::{admonition} {material-regular}`engineering;1.5rem;sd-mr-1` Currently Under Construction
:class: no-icon
Check back for more...
:::

### ToC Trees

```{doc-directive} contents
Insert a table of contents tree of the documents headings.
```

```{doc-directive} toctree
Inserts a Sphinx "Table of Contents" tree, containing a list of (relative) child document paths.
```

### Admonitions

```{doc-directive} admonition
Create a generic "callout" box, containing the content.
```

```{doc-directive} note
Create a "callout" box, specific to notes, containing the content.
```

Other admonitions (same structure as `note`): `attention`, `caution`, `danger`, `error`, `hint`, `important`, `tip`, `warning`.

Sphinx only: `deprecated`, `versionadded`, `versionchanged`.

### Images and Figures

```{doc-directive} image
Insert an image, from a (relative) path or URL.
```

```{doc-directive} figure
Insert an image, from a (relative) path or URL,
with a caption (first paragraph), and optional legend (subsequent content).
```

```{doc-directive} table
Insert a (MyST) table with a caption.
```

### Tables

```{doc-directive} list-table
Create a table from data in a uniform two-level bullet list.
```

```{doc-directive} csv-table
Create a table from CSV (comma-separated values) data.
```

### Code

```{doc-directive} code-block
Syntax highlight a block of code, according to the language.
```

(syntax/roles/special)=

### MyST only

This section contains information about special roles and directives that come bundled with the MyST Parser Sphinx extension.

#### Insert the date and reading time

```{versionadded} 0.14.0
The `sub-ref` role and word counting.
```

You may insert the "last updated" date and estimated reading time into your document via substitution definitions, which can be accessed *via* the `sub-ref` role.

For example:

```markdown
> {sub-ref}`today` | {sub-ref}`wordcount-words` words | {sub-ref}`wordcount-minutes` min read
```

> {sub-ref}`today` | {sub-ref}`wordcount-words` words | {sub-ref}`wordcount-minutes` min read

`today` is replaced by either the date on which the document is parsed, with the format set by <inv:sphinx#today_fmt>, or the `today` variable if set in the configuration file.

The reading speed is computed using the `myst_words_per_minute` configuration (see the [Sphinx configuration options](sphinx/config-options)).
