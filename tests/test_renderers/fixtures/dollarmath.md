Inline Math:
.
$foo$
.
<document source="<src>/index.md">
    <paragraph>
        <math>
            foo
.

Inline Math, multi-line:
.
a $foo
bar$ b
.
<document source="<src>/index.md">
    <paragraph>
        a
        <math>
            foo
            bar
         b
.

Inline Math, multi-line with line break (invalid):
.
a $foo

bar$ b
.
<document source="<src>/index.md">
    <paragraph>
        a $foo
    <paragraph>
        bar$ b
.

Math Block:
.
$$foo$$
.
<document source="<src>/index.md">
    <math_block nowrap="False" number="True" xml:space="preserve">
        foo
.

Math Block With Equation Label:
.
$$foo$$ (abc)
.
<document source="<src>/index.md">
    <target ids="equation-abc">
    <math_block docname="index" label="abc" nowrap="False" number="1" xml:space="preserve">
        foo
.

Math Block multiple:
.
$$
a = 1
$$

$$
b = 2
$$ (a)
.
<document source="<src>/index.md">
    <math_block nowrap="False" number="True" xml:space="preserve">
        a = 1
    <target ids="equation-a">
    <math_block docname="index" label="a" nowrap="False" number="1" xml:space="preserve">
        b = 2
.

Math Block, blank lines at start and end are removed (#614):
.
$$

a = 1

$$

$$

b = 2

$$ (b)
.
<document source="<src>/index.md">
    <math_block nowrap="False" number="True" xml:space="preserve">
        a = 1
    <target ids="equation-b">
    <math_block docname="index" label="b" nowrap="False" number="1" xml:space="preserve">
        b = 2
.

Math Block, interior blank lines and indentation are kept:
.
$$
   \begin{eqnarray}
      y    & = & ax^2 + bx + c \\

      f(x) & = & x^2 + 2xy + y^2
   \end{eqnarray}
$$
.
<document source="<src>/index.md">
    <math_block nowrap="False" number="True" xml:space="preserve">
           \begin{eqnarray}
              y    & = & ax^2 + bx + c \\

              f(x) & = & x^2 + 2xy + y^2
           \end{eqnarray}
.
