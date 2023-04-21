---
py-config:
  splashscreen:
    autoclose: true
  packages:
    - myst-docutils==1.0
    - docutils==0.19
    - pygments
---

# ⚡️ Live Preview

This is a live preview of the MyST Markdown [docutils renderer](docutils.md).
You can edit the text/configuration below and see the live output.

```{py-script}
:file: live_preview.py
```

::::::::{grid} 1 1 2 2

:::::::{grid-item}
:child-align: start

```{raw} html
<div><u><span id="myst-version">myst-parser v</span></u></div>
```

:::::{tab-set}
:class: preview-input-tabs

::::{tab-item} Input text
:class-container: sd-h-100
:class-content: sd-h-100

````{raw} html
<textarea class="pyscript input" id="input_myst">
# Heading 1

Hallo world!

```{note}
An admonition note!
```

[Link to the heading](#heading-1)

## Math

```python
from package import module
module.call("string")
```

## Definition list

term
: definition

## Math

$$\pi = 3.14159$$

## Figures

```{figure} https://via.placeholder.com/150
:width: 100px
:align: center

Figure caption
```

## Tables

```{list-table}
:header-rows: 1
:align: center

* - Header 1
  - Header 2
* - Item 1 a
  - Item 2 a
* - Item 1 b
  - Item 2 b
```
</textarea>
````

::::
::::{tab-item} Configuration (YAML)
:class-container: sd-h-100
:class-content: sd-h-100

<textarea class="pyscript input" id="input_config">
myst_enable_extensions:
- colon_fence
- deflist
- dollarmath
myst_heading_anchors: 2
myst_highlight_code_blocks: true
</textarea>
::::
:::::

:::::::
:::::::{grid-item}
:child-align: start

```{raw} html
<div class="display-flex">
<label for="output_format" class="display-inline-block">Output Format:</label>
<select id="output_format" class="display-inline-block">
  <option value="pseudoxml">AST</option>
  <option value="html5" selected>HTML</option>
  <option value="latex">LaTeX</option>
</select>
</div>
```

::::{tab-set}
:::{tab-item} HTML Render
<div class="pyscript" id="output_html"></div>
:::
:::{tab-item} Raw Output
<textarea class="pyscript output" id="output_raw" readonly="true"></textarea>
:::
:::{tab-item} Warnings
<textarea class="pyscript output" id="output_warnings" readonly="true"></textarea>
:::
::::
:::::::
::::::::
