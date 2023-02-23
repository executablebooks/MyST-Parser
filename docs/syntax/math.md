# Math and equations

Math can be written in the common LaTeX markup.
There are several syntaxes to define inline and block math,
depending on your preference.

## Math role and directive

The `math` {{role}} and {{directive}} are used used to define inline and block math respectively.

The directive supports multiple equations, which should be separated by a blank line.
Each single equation can have multiple aligned lines, which should be separated by `\\` characters, and each line can have multiple `&` characters to align the equations.

The `label` option can also be used to reference the equation later on, with the `eq` role.


:::{myst-example}
Since Pythagoras, we know that {math}`a^2 + b^2 = c^2`.

```{math}
:label: mymath
(a + b)^2 = a^2 + 2ab + b^2

(a + b)^2  &=  (a + b)(a + b) \\
           &=  a^2 + 2ab + b^2
```

The equation {eq}`mymath` is a quadratic equation.
:::


:::{seealso}
Sphinx documentation on the [role](inv:sphinx:rst:role#math) and [directive](inv:sphinx:rst:directive#math),
and [math support for HTML outputs in Sphinx](inv:sphinx#math-support).
:::

## Dollar delimited math

Enabling the [dollarmath](#syntax/math/dollar) extension will allow parsing the following syntax:

- Inline math: `$...$`
- Display (block) math: `$$...$$`

Additionally if `myst_dmath_allow_labels=True` is set (the default):

- Display (block) math with equation label: `$$...$$ (1)`


:::{myst-example}
:highlight: latex

$$
(a + b)^2  &=  (a + b)(a + b) \\
           &=  a^2 + 2ab + b^2
$$ (mymath2)

The equation {eq}`mymath2` is also a quadratic equation.
:::


:::{admonition} Escaping Dollars
:class: tip dropdown

Math can be escaped (negated) by adding a `\` before the first symbol, e.g. `\$a$` renders as \$a\$.
Escaping can also be used inside math, e.g. `$a=\$3$` renders as $a=\$3$.

Conversely `\\` will negate the escaping, so `\\$a$` renders as \\$a$.
:::

## Direct LaTeX Math

Enabling the [amsmath](#syntax/amsmath) extension will directly parse the following top-level math environments:

> equation, multline, gather, align, alignat, flalign, matrix, pmatrix, bmatrix, Bmatrix, vmatrix, Vmatrix, eqnarray.

As expected, environments ending in `*` will not be numbered, for example:

:::{myst-example}
:highlight: latex

\begin{gather*}
a_1=b_1+c_1\\
a_2=b_2+c_2-d_2+e_2
\end{gather*}

\begin{align}
a_{11}& =b_{11}&
  a_{12}& =b_{12}\\
a_{21}& =b_{21}&
  a_{22}& =b_{22}+c_{22}
\end{align}

:::
