---
myst:
  substitutions:
    text: "- text"
    text_with_nest: >
      output
      with *Markdown*
      {{ nested }}
    nested: nested substitution
    admonition: |
      prefix

      ```{note}
      A note {{ nested }}
      ```
    inline_admonition: |
      ```{note}
      Inline note
      ```
    override: Overridden by front matter

---

{{ text_with_nest }}

{{ admonition }}

a {{ text }} b

c {{ text_with_nest }} d

e {{ inline_admonition }} f

{{ conf }}

{{ override }}

This will process the substitution

```{parsed-literal}
{{ text_with_nest }}
```

This will not process the substitution

```python
{{ text_with_nest }}
```

Using env and filters:

{{ env.docname | upper }}

```{toctree}
other.md
```
