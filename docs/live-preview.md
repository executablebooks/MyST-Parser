---
py-config:
  packages:
    - myst-docutils
    - docutils==0.19
    - pygments
  splashscreen:
    autoclose: true
---

# Live Preview

This is a live preview of the MyST Markdown [docutils renderer](docutils.md).
You can edit the text/configuration below and see the live output.
Note that there is no styling applied (that is usually provided by Sphinx themes).

```{py-script}
:file: live_preview.py
```

::::::::{grid} 1 1 1 2

:::::::{grid-item}
:child-align: end

```{raw} html
<div><u><span id="myst-version"></span></u></div>
```

:::::{tab-set}
::::{tab-item} Input text
````{raw} html
<textarea class="pyscript" id="input_myst">
# Heading 1

Hallo world!

```{note}
An admonition note!
```

term
: definition

```{list-table}
:header-rows: 1
* - Header 1
  - Header 2
* - Item 1
  - Item 2
```

```{figure} https://via.placeholder.com/150
:width: 100px

Caption
```
</textarea>
````

::::
::::{tab-item} Configuration (YAML)
<textarea class="pyscript" id="input_config">
myst_enable_extensions:
- colon_fence
- deflist
- dollarmath
myst_highlight_code_blocks: false
embed_stylesheet: true
</textarea>
::::
:::::

:::::::
:::::::{grid-item}
:child-align: end

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
<iframe class="pyscript" id="output_html" readonly="true"></iframe>
:::
:::{tab-item} Raw Output
<textarea class="pyscript" id="output_raw" readonly="true"></textarea>
:::
:::{tab-item} Warnings
<textarea class="pyscript" id="output_warnings" readonly="true"></textarea>
:::
::::
:::::::
::::::::
