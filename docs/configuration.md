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

(syntax/frontmatter)=

## Frontmatter (local) configuration

Frontmatter allows you to specify metadata and options about how a single document should behave or render.
It is a [YAML](https://en.wikipedia.org/wiki/YAML) block at the start of the document, as used for example in [jekyll](https://jekyllrb.com/docs/front-matter/).
The document should start with three or more `---` markers, and YAML is parsed until a closing `---` marker is found:

```yaml
---
key1: value
key2: [value1, value2]
key3:
  subkey1: value
---
```

:::{seealso}
Frontmatter is also used for the [substitution syntax extension](syntax/substitutions),
and can be used to store information for blog posting (see [ablog's myst-parser support](https://ablog.readthedocs.io/en/latest/manual/markdown/)).
:::

The following configuration variables are available to be set in the document frontmatter.
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

(syntax/html_meta)=

### Setting HTML Metadata

The front-matter can contain the special key `html_meta`; a dict with data to add to the generated HTML as [`<meta>` elements](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta).
This is equivalent to using the [meta directive](inv:sphinx#html-meta).

HTML metadata can also be added globally in the `conf.py` *via* the `myst_html_meta` variable, in which case it will be added to all MyST documents.
For each document, the `myst_html_meta` dict will be updated by the document level front-matter `html_meta`, with the front-matter taking precedence.

::::{tab-set}
:::{tab-item} Sphinx Configuration

```python
language = "en"
myst_html_meta = {
    "description lang=en": "metadata description",
    "description lang=fr": "description des métadonnées",
    "keywords": "Sphinx, MyST",
    "property=og:locale":  "en_US"
}
```

:::

:::{tab-item} MyST Front-Matter

```yaml
---
myst:
  html_meta:
    "description lang=en": "metadata description"
    "description lang=fr": "description des métadonnées"
    "keywords": "Sphinx, MyST"
    "property=og:locale": "en_US"
---
```

:::

:::{tab-item} RestructuredText

```restructuredtext
.. meta::
   :description lang=en: metadata description
   :description lang=fr: description des métadonnées
   :keywords: Sphinx, MyST
   :property=og:locale: en_US
```

:::

:::{tab-item} HTML Output

```html
<html lang="en">
  <head>
    <meta content="metadata description" lang="en" name="description" xml:lang="en" />
    <meta content="description des métadonnées" lang="fr" name="description" xml:lang="fr" />
    <meta name="keywords" content="Sphinx, MyST">
    <meta content="en_US" property="og:locale" />
```

:::
::::

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
