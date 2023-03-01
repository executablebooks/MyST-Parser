# Tables

## Markdown syntax

Tables can be written using the standard [Github Flavoured Markdown syntax](https://github.github.com/gfm/#tables-extension-):

:::{myst-example}
| foo | bar |
| --- | --- |
| baz | bim |
:::

Cells in a column can be aligned using the `:` character:

:::{myst-example}
| left | center | right |
| :--- | :----: | ----: |
| a    | b      | c     |
:::

:::{admonition} Aligning cells in Sphinx HTML themes
:class: tip dropdown

Text is aligned by assigning `text-left`, `text-center`, or `text-right` to the cell.
It is then necessary for the theme you are using to include the appropriate css styling.

```html
<table class="colwidths-auto table">
  <thead>
    <tr><th class="text-left head"><p>left</p></th></tr>
  </thead>
  <tbody>
    <tr><td class="text-left"><p>a</p></td></tr>
  </tbody>
</table>
```

:::

## Table with captions

The `table` directive can be used to create a table with a caption:

::::{myst-example}
:::{table} Table caption
:widths: auto
:align: center

| foo | bar |
| --- | --- |
| baz | bim |
:::
::::

The following options are recognized:

:::{admonition} List table options
:class: hint

`align` : "left", "center", or "right"
: The horizontal alignment of the table.

`width` : [length](units/length) or [percentage](units/percentage)
: Sets the width of the table to the specified length or percentage of the line width.
: If omitted, the renderer determines the width of the table based on its contents or the column widths.

`widths` : "auto", "grid", or a list of integers
: Explicitly set column widths. Specifies relative widths if used with the width option.
: "auto" delegates the determination of column widths to the backend renderer.
: "grid" determines column widths from the widths of the input columns (in characters).

:::

## List tables

The `list-table` directive is used to create a table from data in a uniform two-level bullet list.
"Uniform" means that each sublist (second-level list) must contain the same number of list items.

::::{myst-example}
:::{list-table} Frozen Delights!
:widths: 15 10 30
:header-rows: 1

*   - Treat
    - Quantity
    - Description
*   - Albatross
    - 2.99
    - On a stick!
*   - Crunchy Frog
    - 1.49
    - If we took the bones out, it wouldn't be
 crunchy, now would it?
*   - Gannet Ripple
    - 1.99
    - On a stick!
:::
::::

The following options are recognized:


:::{admonition} List table options
:class: hint

`align` : "left", "center", or "right"
: The horizontal alignment of the table.

`header-rows` : integer
: The number of rows of list data to use in the table header. Defaults to 0.

`stub-columns` : integer
: The number of table columns to use as stubs (row titles, on the left). Defaults to 0.

`width` : [length](units/length) or [percentage](units/percentage)
: Sets the width of the table to the specified length or percentage of the line width.
: If omitted, the renderer determines the width of the table based on its contents or the column widths.

`widths` : integer `[integer...]` or "auto"
: A list of relative column widths. The default is equal-width columns (100%/#columns).
: "auto" delegates the determination of column widths to the output builder.

``class``
: A space-separated list of CSS classes to add to the image.

``name``
: A reference target for the admonition (see [cross-referencing](#syntax/referencing)).

:::

## CSV tables

The `csv-table` directive is used to create a table from Comma-Separated-Values data.

:::{myst-example}
```{csv-table} Frozen Delights!
:header: >
:    "Treat", "Quantity", "Description"
:widths: 15, 10, 30

"Albatross", 2.99, "On a stick!"
"Crunchy Frog", 1.49, "If we took the bones out, it wouldn't be crunchy, now would it?"
"Gannet Ripple", 1.99, "On a stick!"
```
:::

The following options are recognized:

:::{admonition} CSV table options
:class: hint

`align` : "left", "center", or "right"
: The horizontal alignment of the table.

`delim` : char | "tab" | "space"
: A one-character string used to separate fields. Defaults to , (comma).
  May be specified as a Unicode code point; see the unicode directive for syntax details.

`encoding` : string
: The text encoding of the external CSV data (file or URL).
  Defaults to the document's input_encoding.

`escape` : char
: A one-character string used to escape the delimiter or quote characters. May be specified as a Unicode code point; see the unicode directive for syntax details. Used when the delimiter is used in an unquoted field, or when quote characters are used within a field. The default is to double-up the character, e.g. "He said, ""Hi!"""

`file` : string (newlines removed)
: The local filesystem path to a CSV data file.

`header` : CSV data
: Supplemental data for the table header, added independently of and before any header-rows from the main CSV data. Must use the same CSV format as the main CSV data.

`header-rows` : integer
: The number of rows of CSV data to use in the table header. Defaults to 0.

`keepspace` : flag
: Treat whitespace immediately following the delimiter as significant. The default is to ignore such whitespace.

`quote` : char
: A one-character string used to quote elements containing the delimiter or which start with the quote character. Defaults to " (quote). May be specified as a Unicode code point; see the unicode directive for syntax details.

`stub-columns` : integer
: The number of table columns to use as stubs (row titles, on the left). Defaults to 0.

`url` : string (whitespace removed)
: An Internet URL reference to a CSV data file.

`widths` : integer, `[integer...]` or "auto"
: A list of relative column widths. The default is equal-width columns (100%/#columns).
: "auto" delegates the determination of column widths to the backend renderer.

`width` : [length](units/length) or [percentage](units/percentage)
: Sets the width of the table to the specified length or percentage of the line width. If omitted, the renderer determines the width of the table based on its contents or the column widths.

``class``
: A space-separated list of CSS classes to add to the image.

``name``
: A reference target for the admonition (see [cross-referencing](#syntax/referencing)).

:::
