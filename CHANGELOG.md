# Changelog

## 0.19.1 - 2023-03-02

🐛 FIX `NoURI` error in doc reference resolution, for texinfo builds (<gh-pr:734>)

## 0.19.0 - 2023-03-01

This release brings a number of exciting new features, improvements, and upgrades 🎉

Full Changelog: [v0.18.1...v0.19.0](https://github.com/executablebooks/MyST-Parser/compare/v0.18.1...v0.19.0)

### 📚 Rewritten documentation

The documentation has been almost completely rewritten,
with a clearer structure, many more examples, rich hover tips, and a new live preview page ⚡️ (powered by [pyscript](https://pyscript.readthedocs.io/), <gh-pr:717>).

The code base API is also now fully documented by [sphinx-autodoc2](https://sphinx-autodoc2.readthedocs.io/), which even allows for MyST docstrings! (<gh-pr:704>).

### ⬆️ Add Sphinx 6 support, drop Sphinx 4

The code base has been updated to support sphinx v6, and is no longer tested against sphinx v4 (<gh-pr:664>)

### 📄 Extended docutils (single-page) support

The `docutils` parser now supports many more features, and improvements to support live previews:

- `myst_suppress_warnings` option added, mirroring Sphinx, to suppress MyST warnings (<gh-pr:655>)
- `myst_meta_html` and `myst_substitutions` options are now supported (<gh-pr:672>)
- `myst_heading_anchors` option is now supported (<gh-pr:678>)
- Math block labels syntax is now supported (<gh-pr:668>)
- Missing directive/role errors errors are now suppressable warnings (<gh-pr:687>)
- Non-fatal directive parsing errors are now suppressable warnings (<gh-pr:682>)
- Most of the extended markdown syntax below is also supported

### 🔗 Extended Markdown links

See the [Extended Markdown links](docs/syntax/cross-referencing.md) section for the full guide.

You can now use standard Markdown link syntax to reference many different types of targets, in a more consistent way.

- `[text](relative/path/myfile.md)` work as previously, to link to files,
  but they can also be relative to source directory: `[text](/path/from/srcdir/myfile.md)`.
  You can also use `<project:file.md>`
- `<path:myfile.txt>` will link specifically to a downloadable file
- `[text](#target)` or `<project:#target>` will link (in order of priority) to any local target, local heading anchor, target in the same project, or intersphinx (inventory) target
- `[text](inv:name:domain:type#target)` will link specifically to a Sphinx inventory target, or to any inventory `<inv:#target>`, and can even use `*` wildcards like `<inv:*:*:*#*.target>`
  - This can even be used in docutils, with the new `myst_inventories` config option
  - The `myst-inv` CLI makes it easy to find the correct inventory target

:::{tip}
It is advised (although not immediately necessary) to prefix all internal references with `#`.
For example, `[...](my-reference)`, should be changed to `[...](#my-reference)`.
:::

### `{}` Attributes syntax

The [`attrs_inline` and `attrs_block`](docs/syntax/optional.md#attributes) extensions allow for common Markdown syntaxes to be extended with greater control over the output.

For example, you can now add classes, ids, and other attributes to inline code, images, and links, as well as to code blocks and directives.

- Inline code: `` `a = 1`{#id .class l=python} ``
- Images: `![image](image.png){#id .class width=100px}`
- Text spans: `[some text]{#id .class}`

A paragraph block can have attributes too:

```markdown
{#id .class}
This is a paragraph with an id and class
```

A code fence can be given line numbers and line emphasis:

````markdown
{#id .class lineno-start=1 emphasize-lines="2,3"}
```python
a = 1
b = 2
c = 3
```
````

A definition list can be turned into a glossary, with referenceable terms:

```markdown
{.glossary}
term name
: Definition of the term
```

Quote blocks can be given an attribution:

```markdown
{attribution="Chris Sewell"}
> My quote
```

### 👌 Miscellaneous improvements

- Nested headings (e.g. inside directives) are now allowed in MyST and are correctly rendered in HTML (<gh-pr:711>)
- The `colon_fence` extension now renders internal content as MyST, rather than as a code block (<gh-pr:713>)
- The `include` directive in MyST documents now supports a `:heading-offset:` option, to offset the heading levels in the included document
- The `myst_heading_slug_func` option now supports setting a `str` which points to a fully qualified function name, e.g. `"module.path.func"` (<gh-pr:696>)
- The `myst_enable_checkboxes` option allows for task list checkboxes to be enabled/disabled (<gh-pr:686>)

### Additional contributions

- 🐛 FIX: Remove unnecessary assert in <gh-pr:659>, thanks to <gh-user:n-peugnet>
- 🔧 ci(deps): setup dependabot (<gh-pr:669>), thanks to <gh-user:mmorel-35>
- 🔧: Depend on typing_extensions only on `Python<3.8` in <gh-pr:642>, thanks to <gh-user:hukkin>

## 0.18.1 - 2022-27-09

Full Changelog: [v0.18.0...v0.18.1](https://github.com/executablebooks/MyST-Parser/compare/v0.18.0...v0.18.1)

- ⬆️ UPGRADE: docutils 0.19 support in <gh-pr:611>
- ✨ NEW: Add `attrs_image` (experimental) extension in <gh-pr:620>
  - e.g. `![image](image.png){#id .class width=100px}`
  - See: [Optional syntax section](docs/syntax/optional.md)
  - **Important**: This is an experimental extension, and may change in future releases

## 0.18.0 - 2022-06-07

Full Changelog: [v0.17.2...v0.18.0](https://github.com/executablebooks/MyST-Parser/compare/v0.17.2...v0.18.0)

This release adds support for Sphinx v5 (dropping v3), restructures the code base into modules, and also restructures the documentation, to make it easier for developers/users to follow.

It also introduces **document-level configuration**  *via* the Markdown front-matter, under the `myst` key.
See the [Local configuration](docs/configuration.md) section for more information.

### Breaking changes

This should not be breaking, for general users of the sphinx extension (with `sphinx>3`),
but will be for anyone directly using the Python API, mainly just requiring changes in import module paths.

The `to_docutils`, `to_html`, `to_tokens` (from `myst_parser/main.py`) and `mock_sphinx_env`/`parse` (from `myst_parser.sphinx_renderer.py`) functions have been removed, since these were primarily for internal testing.
Instead, for single page builds, users should use the docutils parser API/CLI (see [](docs/docutils.md)),
and for testing, functionality has been moved to <https://github.com/chrisjsewell/sphinx-pytest>.

The top-level `html_meta` and `substitutions` front-matter keys have also been deprecated (i.e. they will still work but will emit a warning), as they now form part of the `myst` config, e.g.

```yaml
---
html_meta:
  "description lang=en": "metadata description"
substitutions:
  key1: I'm a **substitution**
---
```

is replaced by:

```yaml
---
myst:
  html_meta:
    "description lang=en": "metadata description"
  substitutions:
    key1: I'm a **substitution**
---
```

### Key PRs

- ♻️📚 Restructure code base and documentation (<gh-pr:566>)
- ⬆️ Drop Sphinx 3 and add Sphinx 5 support (<gh-pr:579>)
- 🐛 FIX: `parse_directive_text` when body followed by options (<gh-pr:580>)
- 🐛 FIX: floor table column widths to integers (<gh-pr:568>), thanks to <gh-user:Jean-Abou-Samra>!

## 0.17.2 - 2022-04-17

Full Changelog: [v0.17.1...v0.17.2](https://github.com/executablebooks/MyST-Parser/compare/v0.17.1...v0.17.2)

- ♻️ REFACTOR: Replace `attrs` by `dataclasses` for configuration (<gh-pr:557>)

## 0.17.1 - 2022-04-15

Full Changelog: [v0.17.0...v0.17.1](https://github.com/executablebooks/MyST-Parser/compare/v0.17.0...v0.17.1)

- 🐛 FIX: Heading anchor resolution for parallel builds (<gh-pr:525>)
- 🔧 MAINTAIN: Move packaging from setuptools to flit (<gh-pr:553>)
- 🔧 MAINTAIN: Directly specify attrs dependency (<gh-pr:555>)

## 0.17.0 - 2022-02-11

This release contains a number of breaking improvements.

Full Changelog: [v0.16.1...v0.17.0](https://github.com/executablebooks/MyST-Parser/compare/v0.16.1...v0.17.0)

### ‼️ Markdown link resolution improvements

**WARNING: This is a breaking change for links that rely on auto-generated anchor links**. You should now [manually enable auto-generated anchor links](https://myst-parser.readthedocs.io/en/latest/syntax/optional.html?highlight=anchor#auto-generated-header-anchors) if you see errors like `WARNING reference target not found`.

Markdown links are of the format `[text](link)`.
MyST-Parser looks to smartly resolve such links, by identifying if they are:

1. A link to an external resource, e.g. `[text](http://example.com)`
2. A link to another source document, e.g. `[text](file.md)`
   - If `header-anchors` are enabled, anchor links are also supported, e.g. `[text](file.md#anchor)`
3. A link to an internal sphinx cross-reference, e.g. `[text](my-reference)`

an additional situation is now supported:

4. A link to a source file, which is not a document, e.g. `[text](file.js)`. This behaves similarly to the sphinx `download` role.

In addition, configuration to more finely tune this behaviour has been added.

- `myst_all_links_external=True`, will make all links be treated as (1)
- `myst_url_schemes=("http", "https")`, sets what URL schemes are treated as (1)
- `myst_ref_domains=("std", "py")`, sets what Sphinx reference domains are checked, when handling (3)

See [Markdown Links and Referencing](docs/syntax/cross-referencing.md) for more information.

### ‼️ Dollarmath is now disabled by default

**WARNING: This is a breaking change for dollar math**. You should now manually enable dollar math (see below).

The default configuration is now `myst_enable_extensions=()`, instead of `myst_enable_extensions=("dollarmath",)`.
If you are using math enclosed in `$` or `$$` in your documents, you should enable `dollarmath` explicitly.

See [Dollar delimited math](docs/syntax/optional.md#math-shortcuts) for more information.

### ⬆️ Drop Python 3.6 support

MyST-Parser now supports, and is tested against, Python 3.7 to 3.10.

### ✨ Add the `strikethrough` extension and `myst_gfm_only` configuration

The `strikethrough` extension allows text within `~~` delimiters to have a strike-through (horizontal line) placed over it.
For example, `~~strikethrough with *emphasis*~~` renders as: ~~strikethrough with *emphasis*~~.

**Important**: This extension is currently only supported for HTML output.

See [Strikethrough](docs/syntax/optional.md#strikethrough) for more information.

The `myst_gfm_only=True` configuration sets up specific configuration, to enable compliance only with [GitHub-flavored Markdown](https://github.github.com/gfm/), including enabling the `strikethrough`, `tasklist` and `linkify` extensions, but disabling support for roles and directives.

### ✨ Add `myst_title_to_header` configuration

Setting `myst_title_to_header=True`, allows for a `title` key in the frontmatter to be used as the document title.
for example:

```md
---
title: My Title with *emphasis*
---
```

would be equivalent to:

```md
# My Title with *emphasis*
```

See [Front matter](docs/configuration.md) for more information.

### 👌 Internal improvements

👌 IMPROVE: Convert nested headings to rubrics.
Headings within directives are not directly supported by sphinx, since they break the structure of the document. Previously myst-parser would emit a `myst.nested_header` warning, but still generate the heading, leading to unexpected outcomes.
Now the warning is still emitted, but also the heading is rendered as a [rubric](https://docutils.sourceforge.io/docs/ref/rst/directives.html#rubric) non-structural heading (i.e. it will not show in the ToC).

Other internal improvements primarily focused in improving support for the for "docutils-only" use, introduced in `v0.16`:

- ♻️ REFACTOR: `default_parser` -> `create_md_parser` in <gh-pr:474>
- 👌 IMPROVE: Add `bullet` attribute to `bullet_list` node in <gh-pr:465>
- 👌 IMPROVE: Use correct renderer for `state.inline_text` in <gh-pr:466>
- 👌 IMPROVE: Docutils parser settings in <gh-pr:476>
- 🐛 FIX: front-matter rendering with docutils in <gh-pr:477>
- 👌 IMPROVE: Code block highlighting in <gh-pr:478>
- 👌 IMPROVE: `note_refname` for docutils internal links in <gh-pr:481>
- 🐛 FIX: Ordered list starting number in <gh-pr:483>
- 👌 IMPROVE: Propagate enumerated list suffix in <gh-pr:484>
- 👌 IMPROVE: `DocutilsRenderer.create_highlighted_code_block` in <gh-pr:488>
- 🐛 FIX: Source line reporting for nested parsing in <gh-pr:490>
- 🔧 MAINTAIN: Implement `MockInliner.parse` in <gh-pr:504>

## 0.16.1 - 2021-12-16

✨ NEW: Add `myst_linkify_fuzzy_links` option.
When using the [`linkify` extension](docs/syntax/optional.md#linkify), this option can be used to disable matching of links that do not contain a schema (such as `http://`).

## 0.16.0 - 2021-12-06

This release contains a number of exciting improvements:

### Upgrade of Markdown parser

`markdown-it-py` has been upgraded to [v2.0.0](https://github.com/executablebooks/markdown-it-py/releases/tag/v2.0.0).
This upgrade brings full compliance with the [CommonMark v0.30 specification](https://spec.commonmark.org/0.30/).

Additionally, `mdit-py-plugins` has been upgraded to [v0.3.0](https://github.com/executablebooks/mdit-py-plugins/releases/tag/v0.3.0).
This improves the parsing of the MyST target syntax, to allow for spaces and additional special characters in the target name,
for example this is now valid:

```md
(a bc   |@<>*./_-+:)=

# Header
```

Also MyST role syntax now supports unlimited length in the role name and new lines in the content.
For example, this is now valid:

```md
{abc}`xy
new line`
```

### Improvements for Docutils-only use

MyST now allows for Docutils-only use (outside of Sphinx), that allows for MyST configuration options to be set via the `docutils.conf` file, or on the command line.

On installing MyST-Parser, the following CLI-commands are made available:

- `myst-docutils-html`: converts MyST to HTML
- `myst-docutils-html5`: converts MyST to HTML5
- `myst-docutils-latex`: converts MyST to LaTeX
- `myst-docutils-xml`: converts MyST to docutils-native XML
- `myst-docutils-pseudoxml`: converts MyST to pseudo-XML (to visualise the AST structure)

You can also install the [myst-docutils](https://pypi.org/project/myst-docutils/) package from `pip`,
which includes no direct install requirements on docutils or sphinx.

See [MyST with Docutils](docs/docutils.md) for more information.

Thanks to help from <gh-user:cpitclaudel>!

### Include MyST files in RST files

With `docutils>=0.17`, the `include` directive has a `parser` option.
This can be used with myst-parser to include MyST files in RST files.

```md
Parse using the docutils only parser:

.. include:: include.md
   :parser: myst_parser.docutils_

Parse using the sphinx parser:

.. include:: include.md
   :parser: myst_parser.sphinx_
```

### Addition of the `fieldlist` syntax extension

Field lists are mappings from field names to field bodies, based on the [reStructureText syntax](https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#field-lists):

```rst
:name only:
:name: body
:name:
  Multiple

  Paragraphs
```

This should eventually allow for MyST Markdown docstrings! (see <https://github.com/executablebooks/MyST-Parser/issues/228>)

See [Field Lists syntax](docs/syntax/optional.md#field-lists) for more information.

### Improvements to table rendering

Tables with no body are now allowed, for example:

```md
| abc | def |
| --- | --- |
```

Also cell alignment HTML classes have now been changed to: `text-left`, `text-center`, or `text-right`, for example:

```md
| left | center | right |
| :--- | :----: | ----: |
| a    | b      | c     |
```

is converted to:

```html
<table class="colwidths-auto">
  <thead>
  <tr>
    <th class="text-left head"><p>left</p></th>
    <th class="text-center head"><p>center</p></th>
    <th class="text-right head"><p>right</p></th>
  </tr>
  </thead>
  <tbody>
  <tr>
    <td class="text-left"><p>a</p></td>
    <td class="text-center"><p>b</p></td>
    <td class="text-right"><p>c</p></td>
  </tr>
  </tbody>
</table>
```

These classes should be supported by most sphinx HTML themes.

See [Tables syntax](docs/syntax/tables.md) for more information.

### Pull Requests

- 🐛 FIX: Add mandatory attributes on `enumerated_list` by <gh-user:cpitclaudel> in <gh-pr:418>
- 📚 DOCS: Add reference to MySTyc in landing page by <gh-user:astrojuanlu> in <gh-pr:413>
- ⬆️ UPGRADE: markdown-it-py v2, mdit-py-plugins v0.3 by <gh-user:chrisjsewell> in <gh-pr:449>
- 👌 IMPROVE: Table rendering by <gh-user:chrisjsewell> in <gh-pr:450>
- 🐛 FIX: Ensure parent files are re-built if `include` file changes by <gh-user:chrisjsewell> in <gh-pr:451>
- 🐛 FIX: Convert empty directive option to `None` by <gh-user:chrisjsewell> in <gh-pr:452>
- 👌 IMPROVE: Add `\\` for hard-breaks in latex by <gh-user:chrisjsewell> in <gh-pr:453>
- 🔧 MAINTAIN: Remove empty "sphinx" extra by <gh-user:hukkin> in <gh-pr:350>
- ✨ NEW: Add `fieldlist` extension by <gh-user:chrisjsewell> in <gh-pr:455>
- ✨ NEW: Add Docutils MyST config and CLI by <gh-user:cpitclaudel> in <gh-pr:426>
- 🔧 MAINTAIN: Add publishing job for `myst-docutils` by <gh-user:chrisjsewell> in <gh-pr:456>
- 🧪 TESTS: Add for `gettext_additional_targets` by <gh-user:jpmckinney> in <gh-pr:459>

### New Contributors

- <gh-user:cpitclaudel> made their first contribution in <gh-pr:418>
- <gh-user:astrojuanlu> made their first contribution in <gh-pr:413>

**Full Changelog**: <https://github.com/executablebooks/MyST-Parser/compare/v0.15.2...v0.16.0>

## 0.15.2 - 2021-08-26

This is mainly a maintenance release that fixes some incompatibilities with `sphinx<3.1`, improvements for compatibility
with `docutils=0.17`, and improvements to robustness.

## 0.15.1 - 2021-06-18

👌 IMPROVE: MathJax compatibility with `nbsphinx`

`nbsphinx` also overrides the MathJax configuration.
For compatibility, `output_area` is added to the list of default processed classes, and the override warning is allowed to be suppressed with `suppress_warnings = ["myst.mathjax"]`.

## 0.15.0 - 2021-06-13

### Upgraded to `sphinx` v4 ⬆️

A principe change in this release is to updates the requirements of myst-parser from `sphinx>=2,<4` to `sphinx>=3,<5`.

### Changed MathJax handling ♻️

Instead of removing all `$` processing for the whole project,
during MyST document parsing, the top-level section is now given the classes `tex2jax_ignore` and `mathjax_ignore` (turning off default MathJax processing of all HTML elements)
and MathJax is then configured to process elements with the `tex2jax_process|mathjax_process|math` classes.

See [the math syntax guide](docs/syntax/optional.md#math-shortcuts) for further information.

### Set URL scheme defaults ‼️

The `myst_url_schemes` default is now: `("http", "https", "mailto", "ftp")`.
This means that only these URL will be considered as external (e.g. `[](https://example.com)`),
and references like `[](prefix:main)` will be considered as internal references.
Set `myst_url_schemes = None`, to revert to the previous default.

### Added `myst_heading_slug_func` option 👌

Use this option to specify a custom function to auto-generate heading anchors (see [Auto-generated header anchors](docs/syntax/optional.md#auto-generated-header-anchors)).

Thanks to <gh-user:jpmckinney>!

## 0.14.0 - 2021-05-04

### Upgrade to `markdown-it-py` v1.0 ⬆️

This release updates the code-base to fully support the [markdown-it-py](https://markdown-it-py.readthedocs.io) `v1.0.0` release.
In particular for users, this update alters the parsing of tables to be consistent with the [Github Flavoured Markdown (GFM) specification](https://github.github.com/gfm/#tables-extension-).

### New Features ✨

- **Task lists** utilise the [markdown-it-py tasklists plugin](inv:markdown_it#md/plugins), and are applied to Markdown list items starting with `[ ]` or `[x]`.

  ```markdown
  - [ ] An item that needs doing
  - [x] An item that is complete
  ```

  Add "tasklist" to the `myst_enable_extensions` configuration to enable.

  See [the optional syntax guide](docs/syntax/optional.md#task-lists) for further information.

- The **`sub-ref`** role has been added for use identical to ReST's `|name|` syntax.

  This allows one to access Sphinx's built-in `|today|`, `|release|` and `|version|` substitutions, and also introduces two new substitutions: `wordcount-words` and `wordcount-minutes`, computed by the markdown-it-py [`wordcount_plugin`](https://github.com/executablebooks/mdit-py-plugins/pull/20).

  ```markdown
  > {sub-ref}`today` | {sub-ref}`wordcount-words` words | {sub-ref}`wordcount-minutes` min read
  ```

  See [the roles syntax guide](docs/syntax/roles-and-directives.md) for further information.

- The **`dmath_double_inline`** configuration option allows display math (i.e. `$$`) within an inline context.
  See [the math syntax guide](docs/syntax/optional.md#math-shortcuts) for further information.

### Remove v0.13 deprecations ‼️

The deprecations made to extension configurations and colon fences in `0.13.0` (see below) have now been removed:

- Configuration variables: `myst_admonition_enable`, `myst_figure_enable`, `myst_dmath_enable`, `myst_amsmath_enable`, `myst_deflist_enable`, `myst_html_img_enable`
- `:::{admonition,class}` -> `:::{admonition}\n:class: class`
- `:::{figure}` -> `:::{figure-md}`

### Fix extraction of nested footnotes 🐛

Previously footnote definitions in block elements like lists would crash the parsing:

```markdown
- [^e]: footnote definition in a block element
```

These are now correctly extracted.

## 0.13.7 - 2021-04-25

👌 IMPROVE: Add warning for nested headers:

Nested headers are not supported within most elements (this is a limitation of the docutils/sphinx document structure), and can lead to unexpected outcomes.
For example in admonitions:

````markdown
```{note}
# Unsupported Header
```
````

A warning (of type `myst.nested_header`) is now emitted when this occurs.

🔧 MAINTAIN: Python 3.9 is now officially supported.

## 0.13.6 - 2021-04-10

🐛 FIX: docutils `v0.17` compatibility

## 0.13.5 - 2021-02-15

- ⬆️ UPGRADE: required markdown-it-py to `v0.6.2`:
  In particular, this fixes missing source line mappings for table rows and their children
- 👌 IMPROVE: Store `rawtext` in AST nodes:
  We now ensure that the raw text is propagated from the Markdown tokens to the Sphinx AST.
  In particular, this is required by the `gettext` builder, to generate translation POT templates.
  Thanks to <gh-user:jpmckinney>!
- ✨ NEW: Add warning types `myst.subtype`:
  All parsing warnings are assigned a type/subtype, and also the messages are appended with them.
  These warning types can be suppressed with the sphinx `suppress_warnings` config option.
  See [How-to suppress warnings](myst-warnings) for more information.

## 0.13.3 - 2021-01-20

Minor fixes:

- 🐛 FIX: front-matter parsing for bibliographic keys
- 🐛 FIX: directive/role name translations
- 👌 IMPROVE: Add warning for multiple footnote definitions

## 0.13.2 - 2021-01-20

✨ NEW: Add `html_admonition` extension

: By adding `"html_admonition"` to `myst_enable_extensions`, you can enable parsing of `<div class="admonition">` HTML blocks to sphinx admonitions.
: This is helpful when you care about viewing the "source" Markdown, such as in Jupyter Notebooks.
: For example:
  ```html
  <div class="admonition note" name="html-admonition">
  <p class="title">This is the **title**</p>
  This is the *content*
  </div>
  ```
: See [the optional syntax guide](docs/syntax/optional.md) for further information.

👌 IMPROVE: Footnotes

: If the label is an integer, then it will always use this integer for the rendered label (i.e. they are manually numbered).
: Add `myst_footnote_transition` configuration, to turn on/off transition line.
: Add `footnotes` class to transition `<hr>` in HTML.
: See [the typography guide](docs/syntax/typography.md) for further information.

👌 IMPROVE: `substitution` extension logic

: Parse inline substitutions without block rules, unless the substitution starts with a directive.

🐛 FIX: Render front-matter as `field_list`

: To improve use by sphinx extensions).

👌 IMPROVE: Code quality

: Add isort and mypy type checking to code base.

(thanks to contributors <gh-user:akhmerov>, <gh-user:tfiers>)

## 0.13.1 - 2020-12-31

👌 Directives can now be used for inline substitutions, e.g.

```md
---
substitutions:
  key: |
    ```{image} img/fun-fish.png
    :alt: fishy
    :height: 20px
    ```
---

An inline image: {{ key }}
```

## 0.13.0 - 2020-12-18

This release makes some major updates to the optional syntaxes.
For full details see [Optional MyST Syntaxes](docs/syntax/optional.md).

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

The `substitution` extension allows you to specify "substitution definitions" in either the `conf.py` (as `myst_substitutions`) and/or individual file's front-matter (front-matter takes precedence), which will then replace substitution references. For example:

```md
---
substitutions:
  key1: definition
---
{{ key1 }}
```

The substitutions are assessed as [jinja2 expressions](http://jinja.palletsprojects.com/) and includes the [Sphinx Environment](inv:sphinx#extdev/envapi) as `env`, so you can do powerful thinks like:

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
: This fixes a bug that would raise errors at parse time if non-string date objects were in front-matter YAML. See <gh-pr:253>

## 0.12.9 - 2020-09-08

✨ NEW: Auto-generate heading anchors.
: This utilises `markdown-it-py`'s `anchors-plugin`, to generate unique anchor "slugs" for each header (up to a certain level),
  and allows them to be referenced *via* a relative path, e.g. `[](./file.md#header-anchor)`, or in the same document, e.g. `[](#header-anchor)`.

  Slugs are generated in the GitHub style ([see here](https://github.com/Flet/github-slugger)); lower-case text, removing punctuation, replacing spaces with `-`, enforce uniqueness *via* suffix enumeration `-1`.

  It is enabled in your `conf.py` *via* `myst_heading_anchors = 2` (sets maximum heading level).

  See [the documentation here](docs/syntax/optional.md#auto-generated-header-anchors).

🐛 FIX: doc reference resolution for singlehtml/latex.
: These reference resolutions are passed to the "missing-reference" event, and require the `node["refdoc"]` attribute to be available, which was missing for `[text](./path/to/file.md)` type references.

## 0.12.7 - 2020-08-31

✨ NEW: Want to include your README.md in the documentation?
: See [including a file from outside the docs folder](howto/include-readme).

(👌 added `relative-docs` option in 0.12.8)

## 0.12.5 - 2020-08-28

✨ NEW: Add Markdown figure syntax
: Setting `myst_figure_enable = True` in your sphinx `conf.py`, combines the above two extended syntaxes,
  to create a fully Markdown compliant version of the `figure` directive.
  See [Markdown Figures](docs/syntax/optional.md#markdown-figures) for details.

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

See the [Definition Lists documentation](https://myst-parser.readthedocs.io/en/latest/syntax/optional.html#definition-lists) for further details.

👌 IMPROVE: mathjax_config override.
: Only `mathjax_config["tex2jax"]` will now be overridden, in order to not interfere with other user configurations, such as adding TeX macros.
  The configuration name has also changed from `myst_override_mathjax` to `myst_update_mathjax`.
  See [Mathjax and math parsing](https://myst-parser.readthedocs.io/en/latest/syntax/syntax.html#mathjax-and-math-parsing) for further details.

## 0.12.2 - 2020-08-25

✨ NEW: Add the `eval-rst` directive

: This directive parses its contents as ReStructuredText, which integrates back into the rest of the document, e.g. for cross-referencing. See [this documentation](https://myst-parser.readthedocs.io/en/latest/syntax/syntax.html#how-directives-parse-content) for further explanation.

  In particular, this addition solves some outstanding user requests:

  - How-to [include rST files into a Markdown file](https://myst-parser.readthedocs.io/en/latest/using/howto.html#include-rst-files-into-a-markdown-file)
  - How-to [Use sphinx.ext.autodoc in Markdown files](https://myst-parser.readthedocs.io/en/latest/using/howto.html#use-sphinx-ext-autodoc-in-markdown-files)

  Thanks to <gh-user:stephenroller> for the contribution 🎉

## 0.12.1 - 2020-08-19

✨ NEW: Add `myst_commonmark_only` config option, for restricting the parser to strict CommonMark (no extensions).

## 0.12.0 - 2020-08-19

### ‼️ BREAKING

If you are using math in your documents, be sure to read the updated [Math syntax guide](https://myst-parser.readthedocs.io/en/latest/syntax/syntax.html#math-shortcuts)!
In particular, the Mathjax configuration is now overridden, such that LaTeX environments will only be rendered if `myst_amsmath_enable=True` is set.

The `myst_math_delimiters` option has also been removed (please open an issue if you would like brackets math parsing to be re-implemented).

In addition the `myst_html_img` option name has been changed to `myst_html_img_enable`.

Some underlying code has also been refactored, to centralise handling of configuration options (see [commit 98573b9](https://github.com/executablebooks/MyST-Parser/commit/98573b9c6e3602ab31d627b5266ae5c1ba2c9e5f)).

### Improved 👌

More configuration options for math parsing (see [MyST configuration options](https://myst-parser.readthedocs.io/en/latest/using/intro.html#myst-configuration-options)).

## 0.11.2 - 2020-07-13

### Added ✨

- `<img src="file.png" width="200px">` tag parsing to sphinx representation, see [the image syntax guide](https://myst-parser.readthedocs.io/en/latest/syntax/syntax.html#images)

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

  See [the syntax guide section](https://myst-parser.readthedocs.io/en/latest/syntax/syntax.html#admonition-directives-special-syntax-optional) for details.

* Direct parsing of [amsmath](https://ctan.org/pkg/amsmath) LaTeX equations (optional).
  See [the syntax guide section](https://myst-parser.readthedocs.io/en/latest/syntax/syntax.html#direct-latex-math-optional) for details.

### Breaking ‼️

* Sphinx configuration options are now set as separate variables, rather than a single dict.
  See [MyST configuration options](https://myst-parser.readthedocs.io/en/latest/using/intro.html#myst-configuration-options) for details.

## 0.10.0 - 2020-07-08

([full changelog](https://github.com/executablebooks/MyST-Parser/compare/v0.9.1...aaed58808af485c29bbbf73c5aac10697bfa08b9))

### Improved 👌

* Support Sphinx version 3 in <gh-pr:197> (<gh-user:chrisjsewell>)
* Update Trove Classifiers in <gh-pr:192> (<gh-user:chrisjsewell>)
* Add functionality to use docutils specialized role in <gh-pr:189> (<gh-user:chrisjsewell>)

### Contributors to this release

([GitHub contributors page for this release](https://github.com/executablebooks/MyST-Parser/graphs/contributors?from=2020-07-20&to=2020-08-07&type=c))

[@AakashGfude](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3AAakashGfude+updated%3A2020-07-20..2020-08-07&type=Issues) | [@asmeurer](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Aasmeurer+updated%3A2020-07-20..2020-08-07&type=Issues) | [@choldgraf](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Acholdgraf+updated%3A2020-07-20..2020-08-07&type=Issues) | [@chrisjsewell](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Achrisjsewell+updated%3A2020-07-20..2020-08-07&type=Issues) | [@codecov](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Acodecov+updated%3A2020-07-20..2020-08-07&type=Issues) | [@webknjaz](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Awebknjaz+updated%3A2020-07-20..2020-08-07&type=Issues) | [@welcome](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Awelcome+updated%3A2020-07-20..2020-08-07&type=Issues)

## Past Releases

### Contributors

([GitHub contributors page for these releases](https://github.com/executablebooks/MyST-Parser/graphs/contributors?from=2020-01-01&to=2020-07-20&type=c))

[@akhmerov](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Aakhmerov+updated%3A2020-01-01..2020-07-20&type=Issues) | [@asmeurer](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Aasmeurer+updated%3A2020-01-01..2020-07-20&type=Issues) | [@certik](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Acertik+updated%3A2020-01-01..2020-07-20&type=Issues) | [@choldgraf](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Acholdgraf+updated%3A2020-01-01..2020-07-20&type=Issues) | [@chrisjsewell](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Achrisjsewell+updated%3A2020-01-01..2020-07-20&type=Issues) | [@codecov](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Acodecov+updated%3A2020-01-01..2020-07-20&type=Issues) | [@dhermes](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Adhermes+updated%3A2020-01-01..2020-07-20&type=Issues) | [@filippo82](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Afilippo82+updated%3A2020-01-01..2020-07-20&type=Issues) | [@jlperla](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Ajlperla+updated%3A2020-01-01..2020-07-20&type=Issues) | [@jstac](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Ajstac+updated%3A2020-01-01..2020-07-20&type=Issues) | [@martinagvilas](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Amartinagvilas+updated%3A2020-01-01..2020-07-20&type=Issues) | [@mlncn](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Amlncn+updated%3A2020-01-01..2020-07-20&type=Issues) | [@mmcky](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Ammcky+updated%3A2020-01-01..2020-07-20&type=Issues) | [@moorepants](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Amoorepants+updated%3A2020-01-01..2020-07-20&type=Issues) | [@najuzilu](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Anajuzilu+updated%3A2020-01-01..2020-07-20&type=Issues) | [@nathancarter](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Anathancarter+updated%3A2020-01-01..2020-07-20&type=Issues) | [@pauleveritt](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Apauleveritt+updated%3A2020-01-01..2020-07-20&type=Issues) | [@phaustin](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Aphaustin+updated%3A2020-01-01..2020-07-20&type=Issues) | [@rossbar](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Arossbar+updated%3A2020-01-01..2020-07-20&type=Issues) | [@rowanc1](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Arowanc1+updated%3A2020-01-01..2020-07-20&type=Issues) | [@sbliven](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Asbliven+updated%3A2020-01-01..2020-07-20&type=Issues) | [@webknjaz](https://github.com/search?q=repo%3Aexecutablebooks%2FMyST-Parser+involves%3Awebknjaz+updated%3A2020-01-01..2020-07-20&type=Issues)
