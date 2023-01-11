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

```{py-script}
:file: live_preview.py
```

:::::{tab-set}
::::{tab-item} Input text
````{raw} html
<textarea class="pyscript" id="input_myst">
# Heading 1

Hallo world!

term
: definition

```{list-table}
:header-rows: 1
* - Header 1
  - Header 2
* - Item 1
  - Item 2
```
</textarea>
````

::::
::::{tab-item} Configuration (YAML)
<textarea class="pyscript" id="input_config">
myst_enable_extensions: [deflist, colon_fence]
myst_highlight_code_blocks: false
embed_stylesheet: false
</textarea>
::::
:::::

<label for="output_format">Output Format:</label>
<select id="output_format">
  <option value="pseudoxml" selected>AST</option>
  <option value="html5">HTML</option>
  <option value="latex">LaTeX</option>
</select>

::::{tab-set}
:::{tab-item} Rendered Output
<textarea class="pyscript" id="output_render" readonly="true"></textarea>
:::
:::{tab-item} Render Warnings
<textarea class="pyscript" id="output_warnings" readonly="true"></textarea>
:::
::::
