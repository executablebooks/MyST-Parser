(myst-docutils)=

# Single Page Builds

```{versionadded} 0.16.0
```

Sphinx, and thus MyST-Parser, is built on top of the [Docutils](https://docutils.sourceforge.io/docs/) package.
MyST-Parser offers a renderer, parser and CLI-interface for working directly with Docutils, independent of Sphinx, as described below.

:::{note}
Since these tools are independent of Sphinx, this means they cannot parse any Sphinx or Sphinx extensions specific roles or directives.
:::

On installing MyST-Parser, the following CLI-commands are made available:

- `myst-docutils-html`: converts MyST to HTML
- `myst-docutils-html5`: converts MyST to HTML5
- `myst-docutils-latex`: converts MyST to LaTeX
- `myst-docutils-xml`: converts MyST to docutils-native XML
- `myst-docutils-pseudoxml`: converts MyST to pseudo-XML (to visualise the AST structure)

Each command can be piped stdin or take a file path as an argument:

```console
$ myst-docutils-html --help
$ echo "Hello World" | myst-docutils-html
$ myst-docutils-html hello-world.md
```

The commands are based on the [Docutils Front-End Tools](https://docutils.sourceforge.io/docs/user/tools.html), and so follow the same argument and options structure, included many of the MyST specific options detailed in [](sphinx/config-options).

:::{dropdown}  Shared Docutils CLI Options
```{docutils-cli-help}
```
:::

:::{versionadded} 0.19.0
`myst-suppress-warnings` replicates the functionality of sphinx's <inv:sphinx#suppress_warnings> for `myst.` warnings in the `docutils` CLI.
:::

The CLI commands can also utilise the [`docutils.conf` configuration file](https://docutils.sourceforge.io/docs/user/config.html) to configure the behaviour of the CLI commands. For example:

```
# These entries affect all processing:
[general]
myst-enable-extensions: deflist,linkify
myst-footnote-transition: no
myst-substitutions:
    key1: value1
    key2: value2

# These entries affect specific HTML output:
[html writers]
embed-stylesheet: no

[html5 writer]
stylesheet-dirs: path/to/html5_polyglot/
stylesheet-path: minimal.css, responsive.css
```

You can also use the {py:class}`myst_parser.docutils_.Parser` class programmatically with the [Docutils publisher API](https://docutils.sourceforge.io/docs/api/publisher.html):

```python
from docutils.core import publish_string
from myst_parser.docutils_ import Parser

source = "hallo world\n: Definition"
output = publish_string(
    source=source,
    writer_name="html5",
    settings_overrides={
        "myst_enable_extensions": ["deflist"],
        "embed_stylesheet": False,
    },
    parser=Parser(),
)
```

Finally, you can include MyST Markdown files within a RestructuredText file, using the [`include` directive](https://docutils.sourceforge.io/docs/ref/rst/directives.html#include):

```rst
.. include:: include.md
   :parser: myst_parser.docutils_
```

```{important}
The `parser` option requires `docutils>=0.17`
```
