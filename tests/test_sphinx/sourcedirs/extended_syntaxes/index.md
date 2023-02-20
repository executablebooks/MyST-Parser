# Test

*disabled*

$a=1$

$$x=5$$

$$x=5$$ (2)

$ a=1 $

a $$c=3$$ b

\begin{equation}
b=2
\end{equation}

```{math}
c=3

d=4
```

Term **1**

: Definition *1*

  second paragraph

Term 2
  ~ Definition 2a
  ~ Definition 2b

Term 3
  :     code block

  : > quote

  : other

{#myid1 .glossary}
term
:  definition

other term
:  other definition

{term}`other term`

:::{figure-md} target
:class: other

![fun-fish](fun-fish.png)

This is a caption in **Markdown**
:::

:::{figure-md} other-target
:class: other

<img src="fun-fish.png" alt="fishy" class="bg-primary mb-1" width="200px">

This is a caption in **Markdown**
:::

:::other
Hallo *there*
:::

linkify URL: www.example.com

- [ ] hallo
- [x] there

Numbered code block:

```typescript
type Result = "pass" | "fail"
```
