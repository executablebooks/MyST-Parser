(sphinx/config-options)=
# Configuration

MyST parsing can be configured at both the global and individual document level,
with the most specific configuration taking precedence.

## Global configuration

Overriding the default configuration at the global level is achieved by specifying variables in the Sphinx `conf.py` file.
All `myst_parser` global configuration variables are prefixed with `myst_`, e.g.

```python
myst_enable_extensions = ["deflist"]
```

:::{seealso}
Configuration in Docutils, in the [](docutils.md) section.
:::

```{myst-config}
:sphinx:
:scope: global
```

### Extensions

Configuration specific to syntax extensions:

```{myst-config}
:sphinx:
:extensions:
:scope: global
```

## Local configuration

```{versionadded} 0.18
```

The following configuration variables are available at the document level.
These can be set in the document [front matter](syntax/frontmatter), under the `myst` key, e.g.

```yaml
---
myst:
  enable_extensions: ["deflist"]
---
```

```{myst-config}
:sphinx:
:scope: local
```

### Extensions

Configuration specific to syntax extensions:

```{myst-config}
:sphinx:
:extensions:
:scope: local
```

## List of syntax extensions

Full details in the [](syntax/extensions) section.

amsmath
: enable direct parsing of [amsmath](https://ctan.org/pkg/amsmath) LaTeX equations

attrs_inline
: Enable inline attribute parsing, [see here](syntax/attributes) for details

colon_fence
: Enable code fences using `:::` delimiters, [see here](syntax/colon_fence) for details

deflist
: Enable definition lists, [see here](syntax/definition-lists) for details

dollarmath
: Enable parsing of dollar `$` and `$$` encapsulated math

fieldlist
: Enable field lists, [see here](syntax/fieldlists) for details

html_admonition
: Convert `<div class="admonition">` elements to sphinx admonition nodes, see the [HTML admonition syntax](syntax/html-admonition) for details

html_image
: Convert HTML `<img>` elements to sphinx image nodes, [see here](syntax/images) for details

inv_link
: Enable the `inv:` schema for Markdown link destinations, [see here](syntax/inv_links) for details

linkify
: Automatically identify "bare" web URLs and add hyperlinks

replacements
: Automatically convert some common typographic texts

smartquotes
: Automatically convert standard quotations to their opening/closing variants

strikethrough
: Enable strikethrough syntax, [see here](syntax/strikethrough) for details

substitution
: Substitute keys, [see here](syntax/substitutions) for details

tasklist
: Add check-boxes to the start of list items, [see here](syntax/tasklists) for details

(howto/warnings)=
(myst-warnings)=
## Build Warnings

Below lists the MyST specific warnings that may be emitted during the build process. These will be prepended to the end of the warning message, e.g.

```
WARNING: Non-consecutive header level increase; H1 to H3 [myst.header]
```

**In general, if your build logs any warnings, you should either fix them or [raise an Issue](https://github.com/executablebooks/MyST-Parser/issues/new/choose) if you think the warning is erroneous.**

However, in some circumstances if you wish to suppress the warning you can use the <inv:sphinx#suppress_warnings> configuration option, e.g.

```python
suppress_warnings = ["myst.header"]
```

Or use `--myst-suppress-warnings="myst.header"` for the [docutils CLI](myst-docutils).

```{myst-warnings}
```
