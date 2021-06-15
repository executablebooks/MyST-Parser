# Common errors and questions

These are common issues and gotchas that people may experience when using the MyST Sphinx extension.

## What markup language should I use inside directives?

If you need to parse content *inside* of another block of content (for example, the
content inside a **note directive**), note that the MyST parser will be used for this
nested parsing as well.

## Why doesn't my role/directive recognize markdown link syntax?

There are some roles/directives that _hard-code_ syntax into
their behavior. For example, many roles allow you to supply titles for links like so:
`` {role}`My title <myref>` ``. While this looks like reStructuredText, the role may
be explicitly expecting the `My title <myref>` structure, and so MyST will behave the same way.
