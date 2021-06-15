# Special roles and directives

This section contains information about special roles and directives that come bundled with the MyST Parser Sphinx extension.

## Insert the date and reading time

```{versionadded} 0.14.0
The `sub-ref` role and word counting.
```

You may insert the "last updated" date and estimated reading time into your document via substitution definitions, which can be accessed *via* the `sub-ref` role.

For example:

```markdown
> {sub-ref}`today` | {sub-ref}`wordcount-words` words | {sub-ref}`wordcount-minutes` min read
```

> {sub-ref}`today` | {sub-ref}`wordcount-words` words | {sub-ref}`wordcount-minutes` min read

`today` is replaced by either the date on which the document is parsed, with the format set by [`today_fmt`](https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-today_fmt), or the `today` variable if set in the configuration file.

The reading speed is computed using the `myst_words_per_minute` configuration (see the [Sphinx configuration options](sphinx/config-options)).
