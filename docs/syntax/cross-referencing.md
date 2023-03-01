(syntax/referencing)=
# Cross-references

MyST-Parser offers powerful cross-referencing features, to link to URLs, documents, headers, figures and more,
that are **portable** across output formats and generate **warnings** when broken.

This page covers the basics of setting up referenceable targets for content and how to reference them.

(syntax/targets)=
## Creating explicit targets

Targets are used to define custom anchors that you can refer to elsewhere in your documentation.

There are three primary ways to create targets:

1. Annotating a syntax block with `(target)=`
2. Annotating a syntax bloc/inline/span with an `{#id}` attribute (using the [attrs_block](#syntax/attributes/block) and [attrs_inline](#syntax/attributes/inline) extensions)
3. Adding a `name` option to a directive

::::{myst-example}

(heading-target)=
### Heading

{#paragraph-target}
This is a paragraph, with an `id` attribute.

This is a [span with an `id` attribute]{#span-target}.

:::{note}
:name: directive-target

This is a directive with a `name` option
:::

[reference1](#heading-target), [reference2](#paragraph-target),
[reference3](#span-target), [reference4](#directive-target)

::::

There are also other ways to create targets, specific to certain directives,
such as [glossaries](#syntax/glossaries) create targets for terms, and [code APIs](#syntax/apis) create targets for objects:

::::{myst-example}
{.glossary}
my other term
: Definition of the term

[Link to a term](<#my other term>)

```{py:class} mypackage.MyClass
:nocontentsentry:
Docstring content
```

[Link to a class](#mypackage.MyClass)
::::

:::{seealso}
The [footnotes section](#syntax/footnotes), covers how to create and link to footnotes,
and the [sphinxcontrib.bibtex](https://pypi.org/project/sphinxcontrib-bibtex/) extension provides a means to reference bibliographies.
:::

(syntax/implicit-targets)=
## Implicit targets

Whole documents can be referenced by path.
Headings within documents can also be assigned an implicit target,
by setting the `myst_heading_anchors` configuration option.
This is should be set to an integer, between 1 and 6, indicating the depth of headings to assign targets to.

The anchor "slugs" are created according to the [GitHub implementation](https://github.com/Flet/github-slugger): heading titles are lower cased, punctuation is removed, spaces are replaced with `-`, and uniqueness is enforced by suffix enumeration.

For example, using `myst_heading_anchors = 2`:

::::{myst-example}
## A heading with slug

## A heading with slug

<project:#a-heading-with-slug>

[Explicit title](#a-heading-with-slug-1)
::::

For more information see the [auto-generated header anchors](#syntax/header-anchors) section.

:::{warning}
In general, it is discouraged to rely on implicit targets,
since they are easy to break, if for example a document/heading is moved or renamed.
:::

## Markdown link syntax

Markdown links come in three forms:

*Autolinks* are [URIs][uri] surrounded by `<` and `>`, which must always have a scheme:

```md
<scheme:path?query#fragment>
```

*Inline links* allow for optional explicit text and titles (in HTML titles are rendered as tooltips):

```md
[Explicit *Markdown* text](destination "optional explicit title")
```

or, if the destination contains spaces,

```md
[Explicit *Markdown* text](<a destination> "optional explicit title")
```

*Reference links* define the destination separately in the document, and can be used multiple times:

```md
[Explicit *Markdown* text][label]
[Another link][label]

[label]: destination "optional explicit title"
```

:::{seealso}
The [CommonMark specification](https://spec.commonmark.org/0.30/#links)
:::

[uri]: https://en.wikipedia.org/wiki/Uniform_Resource_Identifier
[url]: https://en.wikipedia.org/wiki/URL

### Default destination resolution

The destination of a link can resolve to either an **external** target,
such as a [URL] to another website,
or an **internal** target, such as a file, heading or figure within the same project.

By default, MyST will resolve link destinations according to the following rules:

1. Destination beginning with a scheme (e.g. `xxx:`), will be handled according to that scheme:

   {style=lower-roman}
   1. Destinations beginning with `project:` will be treated as internal references
   2. Destinations beginning with `path:` will be treated as downloadable files
   3. Destinations beginning with `inv:` will be treated as intersphinx references
   4. Autolinks or destinations beginning with  `http:`, `https:`, `ftp:`, or `mailto:` will be treated as external [URL] links.

2. Destinations which point to a local file path are treated as links to that file.

   {style=lower-roman}
   1. If the destination is a relative path, it is resolved relative to the current file.
   2. If the destination is an absolute path (starts with `/`), it is resolved relative to the root of the project (i.e. the source directory).
   3. If that path relates to another document in the project (e.g. a `.md` or `.rst` file), then it will link to the first heading in that document.
   4. Links to project documents can also include a `#` fragment identifier, to link to a specific heading in that document.
   5. If the path is to a non-source file (e.g. a `.png` or `.pdf` file), then the link will be to the file itself, e.g. to download it.

3. Destinations beginning with `#` will be treated as internal references.

   {style=lower-roman}
   1. First, explicit targets in the same file are searched for, if not found
   2. Then, implicit targets in the same file are searched for, if not found
   3. Then, explicit targets across the whole project are searched for, if not found
   4. Then, intersphinx references are searched for, if not found
   5. A warning is emitted and the destination is left as an external link.

:::{note}
Local file path resolution and cross-project references are not available in [single page builds](#myst-docutils)
:::

### Explicit vs implicit link text

If the link text is explicitly given, e.g. `[text](#dest)`, then the rendered text will be that.
This text can contain nested inline markup, such as `[*emphasis*](#syntax/emphasis)`{l=md}.

If no text is given or it is an auto-link, e.g. `[](#dest)` or `<project:#dest>`, then MyST will attempt to resolve an implicit text.
For example, if the destination is a heading, then the heading text will be used as the link text,
or if the destination is a figure/table then the caption will be used as the link text.
Otherwise, the link text will be the destination itself.

### Examples

#### Autolinks

:::{myst-example}

:External URL: <https://example.com>
:Internal target reference: <project:#cross-references>
:Internal file reference: <project:../intro.md>
:Internal file -> heading reference: <project:../intro.md#-get-started>
:Downloadable file: <path:example.txt>
:Intersphinx reference: <inv:sphinx:std#index>

:::

#### Inline links with implicit text

:::{myst-example}

:External URL: [](https://example.com)
:Internal target reference: [](#cross-references)
:Internal file reference: [](../intro.md)
:Internal file -> heading reference: [](../intro.md#-get-started)
:Downloadable file: [](example.txt)
:Intersphinx reference: [](inv:sphinx:std#index)

:::

#### Inline links with explicit text

:::{myst-example}

:External URL: [Explicit text](https://example.com)
:Internal target reference: [Explicit text](#cross-references)
:Internal file reference: [Explicit text](../intro.md)
:Internal file -> heading reference: [Explicit text](../intro.md#-get-started)
:Downloadable file: [Explicit text](example.txt)
:Intersphinx reference: [Explicit text](inv:sphinx:std#index)

:::

### Customising external URL resolution

:::{versionadded} 0.19
`myst_url_schemes` now allows for customising how the links are converted to URLs,
and the `attrs_inline` extension can be used to specify certain links as external.
:::

By default, all links which begin with `http:`, `https:`, `ftp:`, or `mailto:` will be treated as external [URL] links.
You can customise this behaviour in a number of ways using [configuration options](../configuration.md).

Most simply, by setting the `myst_all_links_external` configuration option to `True`,
all links will be treated as external [URL] links.

To apply selectively to specific links, you can enable the [attrs_inline](syntax/attributes/inline) extension,
then add an `external` class to the link.\
For example, `[my-external-link](my-external-link){.external}` becomes [my-external-link](my-external-link){.external}.

To specify a custom list of URL schemes, you can set the `myst_url_schemes` configuration option.
By default this is set to `["http", "https", "ftp", "mailto"]`.

As well as being a list of strings, `myst_url_schemes` can also be a dictionary,
where the keys are the URL schemes, and the values define how the links are converted to URLs.
This allows you to customise the conversion of links to URLs for specific schemes, for example:

```python
myst_url_schemes = {
    "http": None,
    "https": None,
    "wiki": "https://en.wikipedia.org/wiki/{{path}}#{{fragment}}",
    "doi": "https://doi.org/{{path}}",
    "gh-issue": {
        "url": "https://github.com/executablebooks/MyST-Parser/issue/{{path}}#{{fragment}}",
        "title": "Issue #{{path}}",
        "classes": ["github"],
    },
}
```

Allows for links such as:

- `[URI](wiki:Uniform_Resource_Identifier#URI_references)` is converted to [URI](wiki:Uniform_Resource_Identifier#URI_references)
- `<doi:10.1186/gm483>` is converted to <doi:10.1186/gm483>
- `<gh-issue:639>` is converted to <gh-issue:639>

:::{tip}
You can also use the [sphinx-tippy](https://sphinx-tippy.readthedocs.io) extension to add rich "hover" tooltips to links.

Adding the `github` class above integrates well the [pydata-sphinx-theme's GitHub link formatting](https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/theme-elements.html#link-shortening-for-git-repository-services)
:::

The value of each scheme can be:

- `None`: the link is converted directly to an external URL.
- A string: the link is converted to an external URL using the string as a template.
- A dictionary: the link is converted to an external URL using the dictionary’s `url` key as a template.
  - The (optional) `title` key is a template for the link’s implicit title, i.e. it is used if the link has no explicit title.
  - The (optional) `classes` key is a list of classes to add to the link.

The templates for `url` and `title` can use variables (enclosed by `{{ }}`), which are substituted for the corresponding parts of the link `<scheme>://<netloc>/<path>;<params>?<query>#<fragment>` (or the full link using `uri`).
For example:

- `scheme`: the URL scheme, e.g. `wiki`.
- `path`: the path part of the URL, e.g. `Uniform_Resource_Identifier`.
- `fragment`: the fragment part of the URL, e.g. `URI_references`.

(syntax/inv_links)=
### Cross-project (intersphinx) links

:::{versionadded} 0.19
:::

Each Sphinx HTML build creates a file named `objects.inv` that contains a mapping from referenceable objects to [URIs][uri] relative to the HTML set’s root.
Each object is uniquely identified by a `domain`, `type`, and `name`.
As well as the relative location, the object can also include implicit `text` for the reference (like the text for a heading).

You can use the `myst-inv` command line tool (installed with `myst_parser`) to visualise and filter any remote URL or local file path to this inventory file (or its parent):

```yaml
# $ myst-inv https://www.sphinx-doc.org/en/master -n index
name: Sphinx
version: 6.2.0
base_url: https://www.sphinx-doc.org/en/master
objects:
  rst:
    role:
      index:
        loc: usage/restructuredtext/directives.html#role-index
        text: null
  std:
    doc:
      index:
        loc: index.html
        text: Welcome
```

To load external inventories into your Sphinx project, you must load the [`sphinx.ext.intersphinx` extension](inv:sphinx#usage/*/intersphinx), and set the `intersphinx_mapping` configuration option.

```python
extensions = ["myst_parser", "sphinx.ext.intersphinx"]
intersphinx_mapping = {
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
}
```

:::{admonition} Docutils configuration
:class: note dropdown

Use the `docutils.conf` configuration file, for more details see [](myst-docutils).

```ini
[general]
myst-inventories:
  sphinx: ["https://www.sphinx-doc.org/en/master", null]
```

:::

you can then reference inventory objects by prefixing the `inv` schema to the destination [URI]: `inv:key:domain:type#name`.

`key`, `domain` and `type` are optional, e.g. for `inv:#name`, all inventories, domains and types will be searched, with a [warning emitted](myst-warnings) if multiple matches are found.

Additionally, `*` is a wildcard which matches zero or characters, e.g. `inv:*:std:doc#a*` will match all `std:doc` objects in all inventories, with a `name` beginning with `a`.
Note, to match to a literal `*` use `\*`.

Here are some examples:

:::{list-table}
:header-rows: 1

* - Type
  - Syntax
  - Rendered

* - Autolink, full
  - `<inv:sphinx:std:doc#index>`{l=myst}
  - <inv:sphinx:std:doc#index>

* - Link, full
  - `[Sphinx](inv:sphinx:std:doc#index)`{l=myst}
  - [Sphinx](inv:sphinx:std:doc#index)

* - Autolink, no type
  - `<inv:sphinx:std#index>`{l=myst}
  - <inv:sphinx:std#index>

* - Autolink, no domain
  - `<inv:sphinx:*:doc#index>`{l=myst}
  - <inv:sphinx:*:doc#index>

* - Autolink, only name
  - `<inv:#*.Sphinx>`{l=myst}
  - <inv:#*.Sphinx>

:::

## Reference roles

Sphinx offers numerous [roles for referencing](#usage/restructuredtext/roles) specific objects.

These can also within MyST documents, although it is recommended to use the Markdown syntax where possible, which is more portable and native to MyST.

:::{myst-example}
- {ref}`syntax/referencing`, {ref}`Explicit text <syntax/referencing>`
- {term}`my other term`
- {doc}`../intro`, {doc}`Explicit text <../intro>`
- {download}`example.txt`, {download}`Explicit text <example.txt>`
- {py:class}`mypackage.MyClass`, {py:class}`Explicit text <mypackage.MyClass>`
- {external:class}`sphinx.application.Sphinx`, {external:class}`Explicit text <sphinx.application.Sphinx>`
- {external+sphinx:ref}`code-examples`, {external+sphinx:ref}`Explicit text <code-examples>`

---

- <project:#syntax/referencing>, [][syntax], [Explicit text][syntax]
- [](<#my other term>)
- <project:../intro.md>, [Explicit text](../intro.md)
- <path:example.txt>, [Explicit text](example.txt)
- <project:#mypackage.MyClass>, [Explicit text](#mypackage.MyClass)
- <inv:#*Sphinx>, [Explicit text](#sphinx.application.Sphinx)
- <inv:sphinx#code-examples>, [Explicit text](inv:sphinx#code-examples)

[syntax]: #syntax/referencing
:::

## Handling invalid references

When building your documentation, it is recommended to run in [nitpicky mode](inv:sphinx:std:confval#nitpicky), which will emit warnings for any invalid references.

you may encounter warnings such as:

```
intro.md:1: WARNING: 'myst' cross-reference target not found: 'reference' [myst.xref_missing]

intro.md:2: WARNING: Multiple matches found for 'duplicate': inter:py:module:duplicate, inter:std:label:duplicate [myst.iref_ambiguous]
```

To fully suppress a specific warning type, you can use the `suppress_warnings` configuration option, in Sphinx’s `conf.py` file:

```python
suppress_warnings = ["myst.xref_missing", "myst.iref_ambiguous"]
```

or in `docutils.conf` or [command-line tool](../docutils.md):

```ini
[general]
myst-suppress-warnings = myst.xref_missing, myst.iref_ambiguous
```

In Sphinx specific reference warnings can also be suppressed, using the <inv:sphinx#nitpick_ignore> and <inv:sphinx#nitpick_ignore_regex> configuration options.

```python
nitpick_ignore = [("myst", "reference")]
```

To handle ambiguous references,
for intersphinx references see the [](syntax/inv_links) section,
or the domains searched for all Markdown references can be restricted globally or per-document using the [`myst_ref_domains` configuration](../configuration.md).

```python
myst_ref_domains = ["std", "py"]
```
