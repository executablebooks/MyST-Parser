Raw
.
foo
.
<document source="notset">
    <paragraph>
        foo
.

Hard-break
.
foo\
bar
.
<document source="notset">
    <paragraph>
        foo
        <raw format="html" xml:space="preserve">
            <br />
        <raw format="latex" xml:space="preserve">
            \\
        bar
.

Strong:
.
**foo**
.
<document source="notset">
    <paragraph>
        <strong>
            foo
.

Emphasis
.
*foo*
.
<document source="notset">
    <paragraph>
        <emphasis>
            foo
.

Escaped Emphasis:
.
\*foo*
.
<document source="notset">
    <paragraph>
        *foo*
.

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

Inline Code:
.
`foo`
.
<document source="notset">
    <paragraph>
        <literal>
            foo
.

Heading:
.
# foo
.
<document source="notset">
    <section ids="foo" names="foo">
        <title>
            foo
.

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

Nested heading
.
> # heading
.
<document source="notset">
    <block_quote>
        <rubric ids="heading" level="1" names="heading">
            heading
.

Block Code:
.
    foo
.
<document source="notset">
    <literal_block classes="code" xml:space="preserve">
        foo
.

Fenced Code:
.
```sh
foo
```
.
<document source="notset">
    <literal_block classes="code sh" xml:space="preserve">
        foo
.

Fenced Code no language:
.
```
foo
```
.
<document source="notset">
    <literal_block classes="code" xml:space="preserve">
        foo
.

Fenced Code no language with trailing whitespace:
.
```  
foo
```
.
<document source="notset">
    <literal_block classes="code" xml:space="preserve">
        foo
.

Image empty:
.
![]()
.
<document source="notset">
    <paragraph>
        <image alt="" uri="">
.

Image with alt and title:
.
![alt](src "title")
.
<document source="notset">
    <paragraph>
        <image alt="alt" title="title" uri="src">
.

Image with escapable html:
.
![alt](http://www.google<>.com)
.
<document source="notset">
    <paragraph>
        <image alt="alt" uri="http://www.google%3C%3E.com">
.

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

Bullet List:
.
- *foo*
* bar
.
<document source="notset">
    <bullet_list bullet="-">
        <list_item>
            <paragraph>
                <emphasis>
                    foo
    <bullet_list bullet="*">
        <list_item>
            <paragraph>
                bar
.

Nested Bullets
.
- a
  - b
    - c
  - d
.
<document source="notset">
    <bullet_list bullet="-">
        <list_item>
            <paragraph>
                a
            <bullet_list bullet="-">
                <list_item>
                    <paragraph>
                        b
                    <bullet_list bullet="-">
                        <list_item>
                            <paragraph>
                                c
                <list_item>
                    <paragraph>
                        d
.

Enumerated List:
.
1. *foo*

1) bar

para

10. starting
11. enumerator
.
<document source="notset">
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                <emphasis>
                    foo
    <enumerated_list enumtype="arabic" prefix="" suffix=")">
        <list_item>
            <paragraph>
                bar
    <paragraph>
        para
    <enumerated_list enumtype="arabic" prefix="" start="10" suffix=".">
        <list_item>
            <paragraph>
                starting
        <list_item>
            <paragraph>
                enumerator
.

Nested Enumrated List:
.
1. a
2. b
    1. c
.
<document source="notset">
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                a
        <list_item>
            <paragraph>
                b
            <enumerated_list enumtype="arabic" prefix="" suffix=".">
                <list_item>
                    <paragraph>
                        c
.

Sphinx Role containing backtick:
.
{code}``a=1{`}``
.
<document source="notset">
    <paragraph>
        <literal classes="code">
            a=1{`}
.

Target:
.
(target)=
.
<document source="notset">
    <target ids="target" names="target">
.

Target with whitespace:
.
(target with space)=
.
<document source="notset">
    <target ids="target-with-space" names="target\ with\ space">
.

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

Block Break:
.
+++ string
.
<document source="notset">
    <comment classes="block_break" xml:space="preserve">
        string
.

Link Reference:
.
[name][key]

[key]: https://www.google.com "a title"
.
<document source="notset">
    <paragraph>
        <reference reftitle="a title" refuri="https://www.google.com">
            name
.

Link Reference short version:
.
[name]

[name]: https://www.google.com "a title"
.
<document source="notset">
    <paragraph>
        <reference reftitle="a title" refuri="https://www.google.com">
            name
.

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
            <reference refname="link">
                a
.

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
            <reference refname="link">
                ref1
            
            [ref2]
    <note>
.

Footnotes:
.
[^a]

[^a]: footnote*text*
.
<document source="notset">
    <paragraph>
        <footnote_reference auto="1" ids="id1" refname="a">
    <transition classes="footnotes">
    <footnote auto="1" ids="a" names="a">
        <paragraph>
            footnote
            <emphasis>
                text
.

Footnotes nested blocks:
.
[^a]

[^a]: footnote*text*

    abc
xyz

    > a

    - b

    c

finish
.
<document source="notset">
    <paragraph>
        <footnote_reference auto="1" ids="id1" refname="a">
    <paragraph>
        finish
    <transition classes="footnotes">
    <footnote auto="1" ids="a" names="a">
        <paragraph>
            footnote
            <emphasis>
                text
        <paragraph>
            abc

            xyz
        <block_quote>
            <paragraph>
                a
        <bullet_list bullet="-">
            <list_item>
                <paragraph>
                    b
        <paragraph>
            c
.

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
    <field_list>
        <field>
            <field_name>
                a
            <field_body>
                <paragraph>
                    <literal>
                        1
        <field>
            <field_name>
                b
            <field_body>
                <paragraph>
                    <literal>
                        foo
        <field>
            <field_name>
                c
            <field_body>
                <paragraph>
                    <literal>
                        {"d": 2}
.

Front Matter Biblio:
.
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
---
.
<document source="notset">
    <field_list>
        <field>
            <field_name>
                author
            <field_body>
                <paragraph>
                    Chris Sewell
        <field>
            <field_name>
                authors
            <field_body>
                <paragraph>
                    Chris Sewell, Chris Hodgraf
        <field>
            <field_name>
                organization
            <field_body>
                <paragraph>
                    EPFL
        <field>
            <field_name>
                address
            <field_body>
                <paragraph>
                    1 Cedar Park Close
                    
                    Thundersley
                    
                    Essex
                    
        <field>
            <field_name>
                contact
            <field_body>
                <paragraph>
                    <reference refuri="https://example.com">
                        https://example.com
        <field>
            <field_name>
                version
            <field_body>
                <paragraph>
                    1.0
        <field>
            <field_name>
                revision
            <field_body>
                <paragraph>
                    1.1
        <field>
            <field_name>
                status
            <field_body>
                <paragraph>
                    good
        <field>
            <field_name>
                date
            <field_body>
                <paragraph>
                    2/12/1985
        <field>
            <field_name>
                copyright
            <field_body>
                <paragraph>
                    MIT
        <field>
            <field_name>
                dedication
            <field_body>
                <paragraph>
                    To my 
                    <emphasis>
                        homies
                    
        <field>
            <field_name>
                abstract
            <field_body>
                <paragraph>
                    Something something 
                    <strong>
                        dark
                     side
        <field>
            <field_name>
                other
            <field_body>
                <paragraph>
                    <literal>
                        Something else
.

Front Matter Bad Yaml:
.
---
a: {
---
.
<document source="notset">
    <system_message level="2" line="1" source="notset" type="WARNING">
        <paragraph>
            Malformed YAML [myst.topmatter]
.

Front Matter HTML Meta
.
---
myst:
    html_meta:
        keywords: Sphinx, documentation, builder
        description lang=en: An amusing story
        description lang=fr: Un histoire amusant
        http-equiv=Content-Type: text/html; charset=ISO-8859-1
---
.
<document source="notset">
    <pending>
        .. internal attributes:
             .transform: docutils.transforms.components.Filter
             .details:
               component: 'writer'
               format: 'html'
               nodes:
                 <meta content="Sphinx, documentation, builder" name="keywords">
    <pending>
        .. internal attributes:
             .transform: docutils.transforms.components.Filter
             .details:
               component: 'writer'
               format: 'html'
               nodes:
                 <meta content="An amusing story" lang="en" name="description">
    <pending>
        .. internal attributes:
             .transform: docutils.transforms.components.Filter
             .details:
               component: 'writer'
               format: 'html'
               nodes:
                 <meta content="Un histoire amusant" lang="fr" name="description">
    <pending>
        .. internal attributes:
             .transform: docutils.transforms.components.Filter
             .details:
               component: 'writer'
               format: 'html'
               nodes:
                 <meta content="text/html; charset=ISO-8859-1" http-equiv="Content-Type">
.

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
    <field_list>
        <field>
            <field_name>
                a
            <field_body>
                <paragraph>
                    <literal>
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
        <literal_block classes="code ::python" xml:space="preserve">
            a = 1
        <paragraph>
            <reference refname="target">
.
