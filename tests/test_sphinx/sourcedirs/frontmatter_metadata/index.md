---
tocdepth: 2
last_review_date: 1970-09-08
reviewers:
  - alice
  - bob
links:
  home: https://example.com
---

# Index

Own metadata: {{ env.metadata[env.docname]["last_review_date"] }}

Own list: {{ env.metadata[env.docname]["reviewers"] }}

Own dict: {{ env.metadata[env.docname]["links"] }}

```{toctree}
other.md
```
