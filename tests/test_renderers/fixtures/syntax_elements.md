---------------------------
Raw
.
foo
.
<document source="notset">
    <paragraph>
        foo
.

---------------------------
Strong:
.
**foo**
.
<document source="notset">
    <paragraph>
        <strong>
            foo
.

---------------------------
Emphasis
.
*foo*
.
<document source="notset">
    <paragraph>
        <emphasis>
            foo
.

---------------------------
Escaped Emphasis:
.
\*foo*
.
<document source="notset">
    <paragraph>
        *foo*
.

--------------------------
Mixed Inline
.
a *b* **c** `abc` \\*
.
<document source="notset">
    <paragraph>
        a
        <emphasis>
            b

        <strong>
            c

        <literal>
            abc
         \*
.

--------------------------
Inline Code:
.
`foo`
.
<document source="notset">
    <paragraph>
        <literal>
            foo
.

--------------------------
Heading:
.
# foo
.
<document source="notset">
    <section ids="foo" names="foo">
        <title>
            foo
.

--------------------------
Heading Levels:
.
# a
## b
### c
# d
.
<document source="notset">
    <section ids="a" names="a">
        <title>
            a
        <section ids="b" names="b">
            <title>
                b
            <section ids="c" names="c">
                <title>
                    c
    <section ids="d" names="d">
        <title>
            d
.

--------------------------
Block Code:
.
```sh
foo
```
.
<document source="notset">
    <literal_block language="sh" xml:space="preserve">
        foo
.

--------------------------
Block Code no language:
.
```
foo
```
.
<document source="notset">
    <literal_block language="default" xml:space="preserve">
        foo
.

--------------------------
Image empty:
.
![]()
.
<document source="notset">
    <paragraph>
        <image alt="" uri="">
.

--------------------------
Image with alt and title:
.
![alt](src "title")
.
<document source="notset">
    <paragraph>
        <image alt="alt" uri="src">
.

--------------------------
Image with escapable html:
.
![alt](http://www.google<>.com)
.
<document source="notset">
    <paragraph>
        <image alt="alt" uri="http://www.google%3C%3E.com">
.

--------------------------
Block Quote:
.
> *foo*
.
<document source="notset">
    <block_quote>
        <paragraph>
            <emphasis>
                foo
.

--------------------------
Bullet List:
.
- *foo*
.
<document source="notset">
    <bullet_list>
        <list_item>
            <paragraph>
                <emphasis>
                    foo
.

--------------------------
Nested Bullets
.
- a
  - b
    - c
  - d
.
<document source="notset">
    <bullet_list>
        <list_item>
            <paragraph>
                a
            <bullet_list>
                <list_item>
                    <paragraph>
                        b
                    <bullet_list>
                        <list_item>
                            <paragraph>
                                c
                <list_item>
                    <paragraph>
                        d
.

--------------------------
Enumerated List:
.
1. *foo*
.
<document source="notset">
    <enumerated_list>
        <list_item>
            <paragraph>
                <emphasis>
                    foo
.

--------------------------
Nested Enumrated List:
.
1. a
2. b
    1. c
.
<document source="notset">
    <enumerated_list>
        <list_item>
            <paragraph>
                a
        <list_item>
            <paragraph>
                b
            <enumerated_list>
                <list_item>
                    <paragraph>
                        c
.

--------------------------
Inline Math:
.
$foo$
.
<document source="notset">
    <paragraph>
        <math>
            foo
.

--------------------------
Math Block:
.
$$foo$$
.
<document source="notset">
    <math_block nowrap="False" number="True" xml:space="preserve">
        foo
.

--------------------------
Math Block With Equation Label:
.
$$foo$$ (abc)
.
<document source="notset">
    <target ids="equation-abc">
    <math_block docname="mock_docname" label="abc" nowrap="False" number="1" xml:space="preserve">
        foo
.

--------------------------
Sphinx Role containing backtick:
.
{code}``a=1{`}``
.
<document source="notset">
    <paragraph>
        <literal classes="code">
            a=1{`}
.

--------------------------
Target:
.
(target)=
.
<document source="notset">
    <target ids="target" names="target">
.

--------------------------
Referencing:
.
(target)=

Title
-----

[alt1](target)

[](target2)

[alt2](https://www.google.com)

[alt3](#target3)
.
<document source="notset">
    <target ids="target" names="target">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <pending_xref refdomain="True" refexplicit="True" reftarget="target" reftype="any" refwarn="True">
                <literal classes="xref any">
                    alt1
        <paragraph>
            <pending_xref refdomain="True" refexplicit="False" reftarget="target2" reftype="any" refwarn="True">
                <literal classes="xref any">
        <paragraph>
            <reference refuri="https://www.google.com">
                alt2
        <paragraph>
            <reference refuri="#target3">
                alt3
.

--------------------------
Comments:
.
line 1
% a comment
line 2
.
<document source="notset">
    <paragraph>
        line 1
    <comment xml:space="preserve">
        a comment
    <paragraph>
        line 2
.

--------------------------
Block Break:
.
+++ string
.
<document source="notset">
    <comment classes="block_break" xml:space="preserve">
        string
.

--------------------------
Link Reference:
.
[name][key]

[key]: https://www.google.com "a title"
.
<document source="notset">
    <paragraph>
        <reference refuri="https://www.google.com" title="a title">
            name
.

--------------------------
Link Reference short version:
.
[name]

[name]: https://www.google.com "a title"
.
<document source="notset">
    <paragraph>
        <reference refuri="https://www.google.com" title="a title">
            name
.

--------------------------
Block Quotes:
.
```{epigraph}
a b*c*

-- a**b**
```
.
<document source="notset">
    <block_quote classes="epigraph">
        <paragraph>
            a b
            <emphasis>
                c
        <attribution>
            a
            <strong>
                b
.

--------------------------
Link Definition in directive:
.
```{note}
[a]
```

[a]: link
.
<document source="notset">
    <note>
        <paragraph>
            <pending_xref refdomain="True" refexplicit="True" reftarget="link" reftype="any" refwarn="True">
                <literal classes="xref any">
                    a
.

--------------------------
Link Definition in nested directives:
.
```{note}
[ref1]: link
```

```{note}
[ref1]
[ref2]
```

```{note}
[ref2]: link
```
.
<document source="notset">
    <note>
    <note>
        <paragraph>
            <pending_xref refdomain="True" refexplicit="True" reftarget="link" reftype="any" refwarn="True">
                <literal classes="xref any">
                    ref1

            [ref2]
    <note>
.

--------------------------
Footnotes:
.
[^a]

[^a]: footnote*text*
.
<document source="notset">
    <paragraph>
        <footnote_reference auto="1" ids="id1" refname="a">
    <transition>
    <footnote auto="1" ids="a" names="a">
        <paragraph>
            footnote
            <emphasis>
                text
.

--------------------------
Front Matter:
.
---
a: 1
b: foo
c:
    d: 2
---
.
<document source="notset">
    <docinfo>
        <field>
            <field_name>
                a
            <field_body>
                1
        <field>
            <field_name>
                b
            <field_body>
                foo
        <field>
            <field_name>
                c
            <field_body>
                {"d": 2}
.

--------------------------
Full Test:
.
---
a: 1
---

(target)=
# header 1
## sub header 1

a *b* **c** `abc`

## sub header 2

x y [a](http://www.xyz.com) z

---

# header 2

```::python {a=1}
a = 1
```

[](target)
.
<document source="notset">
    <docinfo>
        <field>
            <field_name>
                a
            <field_body>
                1
    <target ids="target" names="target">
    <section ids="header-1" names="header\ 1">
        <title>
            header 1
        <section ids="sub-header-1" names="sub\ header\ 1">
            <title>
                sub header 1
            <paragraph>
                a
                <emphasis>
                    b

                <strong>
                    c

                <literal>
                    abc
        <section ids="sub-header-2" names="sub\ header\ 2">
            <title>
                sub header 2
            <paragraph>
                x y
                <reference refuri="http://www.xyz.com">
                    a
                 z
            <transition>
    <section ids="header-2" names="header\ 2">
        <title>
            header 2
        <literal_block language="::python" xml:space="preserve">
            a = 1
        <paragraph>
            <pending_xref refdomain="True" refexplicit="False" reftarget="target" reftype="any" refwarn="True">
                <literal classes="xref any">
.
