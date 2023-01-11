---
py-config:
  splashscreen:
    autoclose: true
  packages:
    - myst-docutils
    - docutils==0.19
    - pygments
---

# Live Preview

This is a live preview of the MyST Markdown [docutils renderer](docutils.md).
You can edit the text/configuration below and see the live output.[^note]

[^note]: Additional styling is usually provided by Sphinx themes.

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

$$\pi = 3.14159$$

```{list-table}
:header-rows: 1
:align: center

* - Header 1
  - Header 2
* - Item 1
  - Item 2
```

```{figure} https://via.placeholder.com/150
:width: 100px
:align: center

Figure caption
```
</textarea>
````

::::
::::{tab-item} Configuration (YAML)
<textarea class="pyscript" id="input_config">
# see: https://docutils.sourceforge.io/docs/user/config.html
myst_enable_extensions:
- colon_fence
- deflist
- dollarmath
myst_highlight_code_blocks: false
embed_stylesheet: true
stylesheet_path:
- minimal.css
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
