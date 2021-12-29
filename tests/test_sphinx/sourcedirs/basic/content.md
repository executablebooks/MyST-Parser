---
author: Chris Sewell
authors: Chris Sewell, Chris Hodgraf
organization: EPFL
address: |
    1 Cedar Park Close
    Thundersley
    Essex
contact: <https://example.com>
version: 1.0
revision: 1.1
status: good
date: 2/12/1985
copyright: MIT
dedication: |
    To my *homies*
abstract:
    Something something **dark** side
other: Something else
other_dict:
  key: value
---

(target)=

# Header

% comment

````{note}
abcd *abc* [google](https://www.google.com)

  ```{warning}
  xyz
  ```

````

```{admonition} Title with [link](target2)
Content
```

(target2)=

```{figure} example.jpg
---
height: 40px
target: https://www.google.com
---
Caption
```

![*alternative text*](example.jpg)

<https://www.google.com>

**{code}`` a=1{`} ``**

{math}`sdfds`

**$a=1$**

$$b=2$$

$$c=2$$ (eq:label)

{eq}`eq:label`

`` a=1{`} ``

| a   | b |
|-----|--:|
| *a* | 2 |
| [link-a](https://google.com) | [link-b](https://python.org) |

this
is
a
paragraph
% a comment 2

this is a second paragraph

- a list
  - a sub list
% a comment 3
- new list?

{ref}`target`  {ref}`target2`

+++ a block break

[name][key]

[key]: https://www.google.com "a title"

```
def func(a, b=1):
    print(a)
```

Special substitution references:

{sub-ref}`wordcount-words` words | {sub-ref}`wordcount-minutes` min read
