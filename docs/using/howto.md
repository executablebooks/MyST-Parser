# How-To Guides

This page describes several common uses of MyST parser and how to accomplish them.

(howto/include-rst)=
## Include rST files into a Markdown file

As explained in [this section](syntax/directives/parsing), all MyST directives will parse their content as Markdown.
Therefore, using the conventional `include` directive, will parse the file contents as Markdown:

````md
```{include} snippets/include-md.md
```
````

```{include} snippets/include-md.md
```

To include rST, we must first "wrap" the directive in the [eval-rst directive](syntax/directives/parsing):

````md
```{eval-rst}
.. include:: snippets/include-rst.rst
```
````

```{eval-rst}
.. include:: snippets/include-rst.rst
```

(howto/include-readme)=
## Include a file from outside the docs folder (like README.md)

You can include a file, including one from outside the project using e.g.:

````md
```{include} ../README.md
```
````

**However**, including a file will not usually resolve local links correctly, like `![](my-image.png)`, since it treats the text as if it originated from the "including file".

As of myst-parser version 0.12.7, a new, experimental feature has been added to resolve such links.
You can now use for example:

````md
Source:
```{include-literal} ../../example.md
:language: md
```
Included:
```{include} ../../example.md
:relative-docs: docs/
:relative-images:
```
````

Source:

```{literalinclude} ../../example-include.md
:language: md
```

Included:

```{include} ../../example-include.md
:relative-docs: docs/
:relative-images:
```

The include here attempts to re-write local links, to reference them from the correct location!
The `relative-docs` must be given the prefix of any links to re-write, to distinguish them from sphinx cross-references.

:::{important}
The current functionality only works for Markdown style images and links.

If you encounter any issues with this feature, please don't hesitate to report it.
:::

(howto/autodoc)=
## Use `sphinx.ext.autodoc` in Markdown files

The [Sphinx extension `autodoc`](sphinx:sphinx.ext.autodoc), which pulls in code documentation from docstrings, is currently hard-coded to parse reStructuredText.
It therefore does not blend in well with MyST, which expects Markdown as input.
However, the special [`eval-rst` directive](syntax/directives/parsing) can be used to "wrap" `autodoc` directives:

````md
```{eval-rst}
.. autoclass:: myst_parser.mocking.MockRSTParser
    :show-inheritance:
    :members: parse
```
````

```{eval-rst}
.. autoclass:: myst_parser.mocking.MockRSTParser
    :show-inheritance:
    :members: parse
```

As with other objects in MyST, this can then be referenced:

- Using the role `` {py:class}`myst_parser.mocking.MockRSTParser` ``: {py:class}`myst_parser.mocking.MockRSTParser`
- Using the Markdown syntax `[MockRSTParser](myst_parser.mocking.MockRSTParser)`: [MockRSTParser](myst_parser.mocking.MockRSTParser)

```{warning}
This expects docstrings to be written in reStructuredText.
We hope to support Markdown in the future, see [GitHub issue #228](https://github.com/executablebooks/MyST-Parser/issues/228).
```

## Show backticks inside raw markdown blocks

If you'd like to show backticks inside of your markdown, you can do so by nesting them
in backticks of a greater length. Markdown will treat the outer-most backticks as the
edges of the "raw" block and everything inside will show up. For example:

``` `` `hi` `` ```  will be rendered as: `` `hi` ``

and

`````
````
```
hi
```
````
`````

will be rendered as:

````
```
hi
```
````

(howto/autosectionlabel)=
## Automatically create targets for section headers

:::{important}

New in `v0.13.0` ✨, myst-parser now provides a separate implementation of `autosectionlabel`, which implements GitHub Markdown style bookmark anchors, like `[](file.md#header-anchor)`.

See the [](syntax/header-anchors) section of extended syntaxes.

:::

If you'd like to *automatically* generate targets for each of your section headers,
check out the [`autosectionlabel`](https://www.sphinx-doc.org/en/master/usage/extensions/autosectionlabel.html)
sphinx feature. You can activate it in your Sphinx site by adding the following to your
`conf.py` file:

```python
extensions = [
    'sphinx.ext.autosectionlabel',
]

# Prefix document path to section labels, to use:
# `path/to/file:heading` instead of just `heading`
autosectionlabel_prefix_document = True
```

So, if you have a page at `myfolder/mypage.md` (relative to your documentation root)
with the following structure:

```md
# Title

## My Subtitle
```

Then the `autosectionlabel` feature will allow you to reference the section headers
like so:

```md
{ref}`path/to/file_1:My Subtitle`
```

(howto/warnings)=
## Suppress warnings

In general, if your build logs any warnings, you should either fix them or [raise an Issue](https://github.com/executablebooks/MyST-Parser/issues/new/choose) if you think the warning is erroneous.
However, in some circumstances if you wish to suppress the warning you can use the [`suppress_warnings`](https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-suppress_warnings) configuration option.
All myst-parser warnings are prepended by their type, e.g. to suppress:

```md
# Title
### Subtitle
```

```
WARNING: Non-consecutive header level increase; 1 to 3 [myst.header]
```

Add to your `conf.py`:

```python
suppress_warnings = ["myst.header"]
```
