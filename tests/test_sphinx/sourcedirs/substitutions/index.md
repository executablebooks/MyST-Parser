---
substitutions:
  text: >
    output
    with *Markdown*
    {{ nested }}
  nested: nested substitution
  admonition: |
    prefix

    ```{note}
    A note {{ nested }}
    ```
  override: Overriden by front matter

---

{{ text }}

{{ admonition }}

b {{ text }} d

{{ conf }}

{{ override }}

This will process the substitution

```{parsed-literal}
{{ text }}
```

This will not process the substitution

```python
{{ text }}
```

Using env and filters:

{{ env.docname | upper }}

```{toctree}
other.md
```
