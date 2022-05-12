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
