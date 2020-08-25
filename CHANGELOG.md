# Change log

## 0.12.2 - 2020-25-08

✨ NEW: Add the `eval-rst` directive

This directive parses its contents as ReStructuredText, which integrates back into the rest of the document, e.g. for cross-referencing. See [this documentation](https://myst-parser.readthedocs.io/en/latest/using/syntax.html#how-directives-parse-content) for further explanation.

In particular, this addition solves some outstanding user requests:

- How-to [include rST files into a Markdown file](https://myst-parser.readthedocs.io/en/latest/using/howto.html#include-rst-files-into-a-markdown-file)
- How-to [Use sphinx.ext.autodoc in Markdown files](https://myst-parser.readthedocs.io/en/latest/using/howto.html#use-sphinx-ext-autodoc-in-markdown-files)

Thanks to [@stephenroller](https://github.com/stephenroller) for the contribution 🎉

## 0.12.1 - 2020-19-08

✨ NEW: Add `myst_commonmark_only` config option, for restricting the parser to strict CommonMark (no extensions).

## 0.12.0 - 2020-19-08

### ‼️ BREAKING

If you are using math in your documents, be sure to read the updated [Math syntax guide](https://myst-parser.readthedocs.io/en/latest/using/syntax.html#math-shortcuts)!
In particular, the Mathjax configuration is now overridden, such that LaTeX environments will only be rendered if `myst_amsmath_enable=True` is set.

The `myst_math_delimiters` option has also been removed (please open an issue if you would like brackets math parsing to be re-implemented).

In addition the `myst_html_img` option name has been changed to `myst_html_img_enable`.

Some underlying code has also been refactored, to centralise handling of configuration options (see [commit 98573b9](https://github.com/executablebooks/MyST-Parser/commit/98573b9c6e3602ab31d627b5266ae5c1ba2c9e5f)).

### Improved 👌

More configuration options for math parsing (see [MyST configuration options](https://myst-parser.readthedocs.io/en/latest/using/intro.html#myst-configuration-options)).

## 0.11.2 - 2020-13-07

### Added ✨

- `<img src="file.png" width="200px">` tag parsing to sphinx representation, see [the image syntax guide](https://myst-parser.readthedocs.io/en/latest/using/syntax.html#images)

### Improved 👌

- `[title](link)` syntax now works with intersphinx references.
  Recognised URI schemas can also be configured, see the [configuration options](https://myst-parser.readthedocs.io/en/latest/using/intro.html#myst-configuration-options)

## 0.11.1 - 2020-12-07

### Fix

- Correctly pin required minimum markdown-it-py version

## 0.11.0 - 2020-12-07

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

## 0.10.0 - 2020-08-07

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
