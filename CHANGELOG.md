# Changelog

## 0.13.0 - 2020-12-18

This release makes some major updates to the optional syntaxes.
For full details see [Optional MyST Syntaxes](docs/using/syntax-optional.md).

### 🗑 Deprecations

`myst_enable_extensions = ["dollarmath", ...]` now replaces and deprecates individual enable configuration variables: `admonition_enable` -> `"colon_fence"`, `figure_enable` -> `"colon_fence"`, `dmath_enable` -> `"dollarmath"`, `amsmath` -> `"colon_fence"`, `deflist_enable` -> `"deflist"`, `html_img_enable` -> `"html_image"`.

The `colon_fence` extension (replacing `admonition_enable`) now works exactly the same as normal ```` ``` ```` code fences, but using `:::` delimiters. This is helpful for directives that contain Markdown text, for example:

```md
:::{admonition} The title
:class: note

This note contains *Markdown*
:::
```

### ✨ New

The `smartquotes` extension will automatically convert standard quotations to their opening/closing variants:

- `'single quotes'`: ‘single quotes’
- `"double quotes"`:  “double quotes”

The `linkify` extension will automatically identify “bare” web URLs, like `www.example.com`,  and add hyperlinks; www.example.com.
This extension requires that [linkify-it-py](https://github.com/tsutsu3/linkify-it-py) is installed.

The `replacements` extension will automatically convert some common typographic texts, such as `+-` -> `±`.

The `substitutions` extension allows you to specify "substitution definitions" in either the `conf.py` (as `myst_substitutions`) and/or individual file's front-matter (front-matter takes precedence), which will then replace substitution references. For example:

```md
---
substitutions:
  key1: definition
---
{{ key1 }}
```

The substitutions are assessed as [jinja2 expressions](http://jinja.palletsprojects.com/) and includes the [Sphinx Environment](https://www.sphinx-doc.org/en/master/extdev/envapi.html) as `env`, so you can do powerful thinks like:

```
{{ [key1, env.docname] | join('/') }}
```

The `figure-md` directive has been added (replacing `enable_figure`), which parses a "Markdown friendly" figure (used with the `colon_fence` extension):

```md
:::{figure-md} fig-target
:class: myclass

<img src="img/fun-fish.png" alt="fishy" class="bg-primary mb-1" width="200px">

This is a caption in **Markdown**
:::
```

### 👌 Improvements

Using the `html_image` extension, HTML images are now processed for both blocks and (now) inline.

So you can correctly do, for example:

```md
I’m an inline image: <img src="img/fun-fish.png" height="20px">

| table column                              |
| ----------------------------------------- |
| <img src="img/fun-fish.png" width="20px"> |
```

## 0.12.10 - 2020-09-21

🐛 FIX: allow dates to be parsed in frontmatter.
: This fixes a bug that would raise errors at parse time if non-string date objects were in front-matter YAML. See [#253](https://github.com/executablebooks/MyST-Parser/pull/253)

## 0.12.9 - 2020-09-08

✨ NEW: Auto-generate heading anchors.
: This utilises `markdown-it-py`'s `anchors-plugin`, to generate unique anchor "slugs" for each header (up to a certain level),
  and allows them to be referenced *via* a relative path, e.g. `[](./file.md#header-anchor)`, or in the same document, e.g. `[](#header-anchor)`.

  Slugs are generated in the GitHub style ([see here](https://github.com/Flet/github-slugger)); lower-case text, removing punctuation, replacing spaces with `-`, enforce uniqueness *via* suffix enumeration `-1`.

  It is enabled in your `conf.py` *via* `myst_heading_anchors = 2` (sets maximum heading level).

  See [the documentation here](docs/using/syntax-optional.md#auto-generated-header-anchors).

🐛 FIX: doc reference resolution for singlehtml/latex.
: These reference resolutions are passed to the "missing-reference" event, and require the `node["refdoc"]` attribute to be available, which was missing for `[text](./path/to/file.md)` type references.

## 0.12.7 - 2020-08-31

✨ NEW: Want to include your README.md in the documentation?
: See [including a file from outside the docs folder](docs/using/howto.md).

(👌 added `relative-docs` option in 0.12.8)

## 0.12.5 - 2020-08-28

✨ NEW: Add Markdown figure syntax
: Setting `myst_figure_enable = True` in your sphinx `conf.py`, combines the above two extended syntaxes,
  to create a fully Markdown compliant version of the `figure` directive.
  See [Markdown Figures](docs/using/syntax-optional.md#markdown-figures) for details.

(👌 formatting of caption improved in 0.12.6)

## 0.12.4 - 2020-08-27

👌 IMPROVE: the mathjax extension is now only overridden if strictly necessary (to support dollar and ams math), and the override is more precise, to mitigate any unwanted side-effects

## 0.12.3 - 2020-08-26

✨ NEW: Add definition lists.
: This addition, enabled by `myst_deflist_enable = True`, allows for "Pandoc style" definition lists to be parsed and rendered, e.g.

```md
Term 1
: Definition
```

See the [Definition Lists documentation](https://myst-parser.readthedocs.io/en/latest/using/syntax-optional.html#definition-lists) for further details.

👌 IMPROVE: mathjax_config override.
: Only `mathjax_config["tex2jax"]` will now be overridden, in order to not interfere with other user configurations, such as adding TeX macros.
  The configuration name has also changed from `myst_override_mathjax` to `myst_update_mathjax`.
  See [Mathjax and math parsing](https://myst-parser.readthedocs.io/en/latest/using/syntax.html#mathjax-and-math-parsing) for further details.

## 0.12.2 - 2020-08-25

✨ NEW: Add the `eval-rst` directive

: This directive parses its contents as ReStructuredText, which integrates back into the rest of the document, e.g. for cross-referencing. See [this documentation](https://myst-parser.readthedocs.io/en/latest/using/syntax.html#how-directives-parse-content) for further explanation.

  In particular, this addition solves some outstanding user requests:

  - How-to [include rST files into a Markdown file](https://myst-parser.readthedocs.io/en/latest/using/howto.html#include-rst-files-into-a-markdown-file)
  - How-to [Use sphinx.ext.autodoc in Markdown files](https://myst-parser.readthedocs.io/en/latest/using/howto.html#use-sphinx-ext-autodoc-in-markdown-files)

  Thanks to [@stephenroller](https://github.com/stephenroller) for the contribution 🎉

## 0.12.1 - 2020-08-19

✨ NEW: Add `myst_commonmark_only` config option, for restricting the parser to strict CommonMark (no extensions).

## 0.12.0 - 2020-08-19

### ‼️ BREAKING

If you are using math in your documents, be sure to read the updated [Math syntax guide](https://myst-parser.readthedocs.io/en/latest/using/syntax.html#math-shortcuts)!
In particular, the Mathjax configuration is now overridden, such that LaTeX environments will only be rendered if `myst_amsmath_enable=True` is set.

The `myst_math_delimiters` option has also been removed (please open an issue if you would like brackets math parsing to be re-implemented).

In addition the `myst_html_img` option name has been changed to `myst_html_img_enable`.

Some underlying code has also been refactored, to centralise handling of configuration options (see [commit 98573b9](https://github.com/executablebooks/MyST-Parser/commit/98573b9c6e3602ab31d627b5266ae5c1ba2c9e5f)).

### Improved 👌

More configuration options for math parsing (see [MyST configuration options](https://myst-parser.readthedocs.io/en/latest/using/intro.html#myst-configuration-options)).

## 0.11.2 - 2020-07-13

### Added ✨

- `<img src="file.png" width="200px">` tag parsing to sphinx representation, see [the image syntax guide](https://myst-parser.readthedocs.io/en/latest/using/syntax.html#images)

### Improved 👌

- `[title](link)` syntax now works with intersphinx references.
  Recognised URI schemas can also be configured, see the [configuration options](https://myst-parser.readthedocs.io/en/latest/using/intro.html#myst-configuration-options)

## 0.11.1 - 2020-07-12

### Fix

- Correctly pin required minimum markdown-it-py version

## 0.11.0 - 2020-07-12

### Added ✨

* Special admonition directive syntax (optional):

  ```md
  :::{note}
  This text is **standard** _Markdown_
  :::
  ```

  See [the syntax guide section](https://myst-parser.readthedocs.io/en/latest/using/syntax.html#admonition-directives-special-syntax-optional) for details.

* Direct parsing of [amsmath](https://ctan.org/pkg/amsmath) LaTeX equations (optional).
  See [the syntax guide section](https://myst-parser.readthedocs.io/en/latest/using/syntax.html#direct-latex-math-optional) for details.

### Breaking ‼️

* Sphinx configuration options are now set as separate variables, rather than a single dict.
  See [MyST configuration options](https://myst-parser.readthedocs.io/en/latest/using/intro.html#myst-configuration-options) for details.

## 0.10.0 - 2020-07-08

([full changelog](https://github.com/executablebooks/MyST-Parser/compare/v0.9.1...aaed58808af485c29bbbf73c5aac10697bfa08b9))

### Improved 👌

* Support Sphinx version 3 [#197](https://github.com/executablebooks/MyST-Parser/pull/197) ([@chrisjsewell](https://github.com/chrisjsewell))
* Update Trove Classifiers [#192](https://github.com/executablebooks/MyST-Parser/pull/192) ([@chrisjsewell](https://github.com/chrisjsewell))
* Add functionality to use docutils specialized role [#189](https://github.com/executablebooks/MyST-Parser/pull/189) ([@chrisjsewell](https://github.com/chrisjsewell))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/executablebooks/MyST-Parser/graphs/contributors?from=2020-07-20&to=2020-08-07&type=c))

[@AakashGfude](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3AAakashGfude+updated%3A2020-07-20..2020-08-07&type=Issues) | [@asmeurer](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Aasmeurer+updated%3A2020-07-20..2020-08-07&type=Issues) | [@choldgraf](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Acholdgraf+updated%3A2020-07-20..2020-08-07&type=Issues) | [@chrisjsewell](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Achrisjsewell+updated%3A2020-07-20..2020-08-07&type=Issues) | [@codecov](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Acodecov+updated%3A2020-07-20..2020-08-07&type=Issues) | [@webknjaz](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Awebknjaz+updated%3A2020-07-20..2020-08-07&type=Issues) | [@welcome](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Awelcome+updated%3A2020-07-20..2020-08-07&type=Issues)

## Past Releases

### Contributors

([GitHub contributors page for these releases](https://github.com/executablebooks/MyST-Parser/graphs/contributors?from=2020-01-01&to=2020-07-20&type=c))

[@akhmerov](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Aakhmerov+updated%3A2020-01-01..2020-07-20&type=Issues) | [@asmeurer](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Aasmeurer+updated%3A2020-01-01..2020-07-20&type=Issues) | [@certik](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Acertik+updated%3A2020-01-01..2020-07-20&type=Issues) | [@choldgraf](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Acholdgraf+updated%3A2020-01-01..2020-07-20&type=Issues) | [@chrisjsewell](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Achrisjsewell+updated%3A2020-01-01..2020-07-20&type=Issues) | [@codecov](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Acodecov+updated%3A2020-01-01..2020-07-20&type=Issues) | [@dhermes](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Adhermes+updated%3A2020-01-01..2020-07-20&type=Issues) | [@filippo82](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Afilippo82+updated%3A2020-01-01..2020-07-20&type=Issues) | [@jlperla](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Ajlperla+updated%3A2020-01-01..2020-07-20&type=Issues) | [@jstac](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Ajstac+updated%3A2020-01-01..2020-07-20&type=Issues) | [@martinagvilas](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Amartinagvilas+updated%3A2020-01-01..2020-07-20&type=Issues) | [@mlncn](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Amlncn+updated%3A2020-01-01..2020-07-20&type=Issues) | [@mmcky](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Ammcky+updated%3A2020-01-01..2020-07-20&type=Issues) | [@moorepants](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Amoorepants+updated%3A2020-01-01..2020-07-20&type=Issues) | [@najuzilu](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Anajuzilu+updated%3A2020-01-01..2020-07-20&type=Issues) | [@nathancarter](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Anathancarter+updated%3A2020-01-01..2020-07-20&type=Issues) | [@pauleveritt](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Apauleveritt+updated%3A2020-01-01..2020-07-20&type=Issues) | [@phaustin](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Aphaustin+updated%3A2020-01-01..2020-07-20&type=Issues) | [@rossbar](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Arossbar+updated%3A2020-01-01..2020-07-20&type=Issues) | [@rowanc1](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Arowanc1+updated%3A2020-01-01..2020-07-20&type=Issues) | [@sbliven](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Asbliven+updated%3A2020-01-01..2020-07-20&type=Issues) | [@webknjaz](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Awebknjaz+updated%3A2020-01-01..2020-07-20&type=Issues)
