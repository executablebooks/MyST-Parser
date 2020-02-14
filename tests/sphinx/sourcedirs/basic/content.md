(target)=

# Header

% comment

````{note}
abcd *abc* [google](https://www.google.com)

  ```{warning}
  xyz
  ```

````

(target2)=

```{figure} example.jpg
---
height: 40px
---
Caption
```

![*alternative text*](example.jpg)

<https://www.google.com>

**{code}`` a=1{`} ``**

{math}`sdfds`

**$a=1$**

$$b=2$$

`` a=1{`} ``

| a   | b |
|-----|---|
| *a* | 2 |

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

[name][key]

[key]: https://www.google.com "a title"

```
def func(a, b=1):
    print(a)
```
