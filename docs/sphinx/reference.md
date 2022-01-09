(sphinx/config-options)=
# Sphinx configuration options

You can control the behaviour of the MyST parser in Sphinx by modifying your `conf.py` file.
To do so, use the keywords beginning `myst_`.

`````{list-table}
:header-rows: 1

* - Option
  - Default
  - Description
* - `myst_commonmark_only`
  - `False`
  - If `True` convert text as strict CommonMark (all options below are then ignored). Note that strict CommonMark is unable to parse any directives, including the `toctree` directive, thus limiting MyST parser to single-page documentations. Use in conjunction with [sphinx-external-toc](https://github.com/executablebooks/sphinx-external-toc) Sphinx extension to counter this limitation.
* - `myst_disable_syntax`
  - ()
  - List of markdown syntax elements to disable, see the [markdown-it parser guide](markdown_it:using).
* - `myst_enable_extensions`
  - `["dollarmath"]`
  - Enable Markdown extensions, [see here](../syntax/optional.md) for details.
* - `myst_all_links_external`
  - `False`
  - If `True`, all Markdown links `[text](link)` are treated as external.
* - `myst_url_schemes`
  - `None`
  - [URI schemes](https://en.wikipedia.org/wiki/List_of_URI_schemes) that will be recognised as external URLs in `[](scheme:loc)` syntax, or set `None` to recognise all.
    Other links will be resolved as internal cross-references.
* - `myst_ref_domains`
  - `None`
  - If a list, then only these [sphinx domains](sphinx:domain) will be searched for when resolving Markdown links like `[text](reference)`.
* - `myst_linkify_fuzzy_links`
  - `True`
  - If `False`, only links that contain a scheme (such as `http`) will be recognised as external links.
* - `myst_title_to_header`
  - `False`
  - If `True`, the `title` key of a document front-matter is converted to a header at the top of the document.
* - `myst_heading_anchors`
  - `None`
  - Enable auto-generated heading anchors, up to a maximum level, [see here](syntax/header-anchors) for details.
* - `myst_heading_slug_func`
  - `None`
  - Use the specified function to auto-generate heading anchors, [see here](syntax/header-anchors) for details.
* - `myst_number_code_blocks`
  - `()`
  - Add line numbers to code blocks with these languages, [see here](syntax/code-blocks) for details.
* - `myst_substitutions`
  - `{}`
  - A mapping of keys to substitutions, used globally for all MyST documents when the "substitution" extension is enabled.
* - `myst_html_meta`
  - `{}`
  - A mapping of keys to HTML metadata, used globally for all MyST documents. See [](syntax/html_meta).
* - `myst_footnote_transition`
  - `True`
  - Place a transition before any footnotes.
* - `myst_words_per_minute`
  - `200`
  - Reading speed used to calculate `` {sub-ref}`wordcount-minutes` ``
`````

List of extensions:

- "amsmath": enable direct parsing of [amsmath](https://ctan.org/pkg/amsmath) LaTeX equations
- "colon_fence": Enable code fences using `:::` delimiters, [see here](syntax/colon_fence) for details
- "deflist": Enable definition lists, [see here](syntax/definition-lists) for details
- "dollarmath": Enable parsing of dollar `$` and `$$` encapsulated math
- "html_admonition": Convert `<div class="admonition">` elements to sphinx admonition nodes, see the [HTML admonition syntax](syntax/html-admonition) for details
- "fieldlist": Enable field lists, [see here](syntax/fieldlists) for details
- "html_image": Convert HTML `<img>` elements to sphinx image nodes, see the [image syntax](syntax/images) for details
- "linkify": automatically identify "bare" web URLs and add hyperlinks
- "replacements": automatically convert some common typographic texts
- "smartquotes": automatically convert standard quotations to their opening/closing variants
- "substitution": substitute keys, see the [substitutions syntax](syntax/substitutions) for details
- "tasklist": add check-boxes to the start of list items, see the [tasklist syntax](syntax/tasklists) for details

Math specific, when `"dollarmath"` activated, see the [Math syntax](syntax/math) for more details:

`````{list-table}
:header-rows: 1

* - Option
  - Default
  - Description
* - `myst_dmath_double_inline`
  - `False`
  - Allow display math (i.e. `$$`) within an inline context
* - `myst_dmath_allow_labels`
  - `True`
  - Parse `$$...$$ (label)` syntax
* - `myst_dmath_allow_space`
  - `True`
  - If False then inline math will only be parsed if there are no initial/final spaces,
    e.g. `$a$` but not `$ a$` or `$a $`
* - `myst_dmath_allow_digits`
  - `True`
  - If False then inline math will only be parsed if there are no initial/final digits,
    e.g. `$a$` but not `1$a$` or `$a$2` (this is useful for using `$` as currency)
* - `myst_amsmath_enable`
  - `False`
  - Enable direct parsing of [amsmath LaTeX environments](https://ctan.org/pkg/amsmath)
* - `myst_update_mathjax`
  - `True`
  - If using [sphinx.ext.mathjax](https://www.sphinx-doc.org/en/master/usage/extensions/math.html#module-sphinx.ext.mathjax) (the default) then `mathjax_config` will be updated,
  to ignore `$` delimiters and LaTeX environments, which should instead be handled by
  `myst_dmath_enable` and `myst_amsmath_enable` respectively.
`````

## Disable markdown syntax for the parser

If you'd like to either enable or disable custom markdown syntax, use `myst_disable_syntax`.
Anything in this list will no longer be parsed by the MyST parser.

For example, to disable the `emphasis` in-line syntax, use this configuration:

```python
myst_disable_syntax = ["emphasis"]
```

emphasis syntax will now be disabled. For example, the following will be rendered
*without* any italics:

```md
*emphasis is now disabled*
```

For a list of all the syntax elements you can disable, see the [markdown-it parser guide](markdown_it:using).
