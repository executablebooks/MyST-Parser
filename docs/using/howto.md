# How-to

This page describes several common uses of MyST parser and how to accomplish them.

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

(autosectionlabel)=
## Automatically create targets for section headers

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
