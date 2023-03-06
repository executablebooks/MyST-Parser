[external] 
.
[alt2](https://www.google.com)
[](https://www.google.com)
<https://www.google.com>
.
<document source="<src>/index.md">
    <paragraph>
        <reference refuri="https://www.google.com">
            alt2

        <reference refuri="https://www.google.com">

        <reference refuri="https://www.google.com">
            https://www.google.com
.

[missing] 
.
[](#test)
<project:#test>
[explicit](#test)
[](<#name with spaces>)
.
<document source="<src>/index.md">
    <paragraph>
        <reference id_link="True" refid="test">
            <system_message level="2" line="1" source="<src>/index.md" type="WARNING">
                <paragraph>
                    'myst' reference target not found: 'test' [myst.xref_missing]

        <reference id_link="True" refid="test">
            <system_message level="2" line="1" source="<src>/index.md" type="WARNING">
                <paragraph>
                    'myst' reference target not found: 'test' [myst.xref_missing]

        <reference id_link="True" refid="test">
            explicit
            <system_message level="2" line="1" source="<src>/index.md" type="WARNING">
                <paragraph>
                    'myst' reference target not found: 'test' [myst.xref_missing]

        <reference id_link="True" refid="name%20with%20spaces">
            <system_message level="2" line="1" source="<src>/index.md" type="WARNING">
                <paragraph>
                    'myst' reference target not found: 'name with spaces' [myst.xref_missing]


<src>/index.md:1: (WARNING/2) 'myst' reference target not found: 'test' [myst.xref_missing]
<src>/index.md:1: (WARNING/2) 'myst' reference target not found: 'test' [myst.xref_missing]
<src>/index.md:1: (WARNING/2) 'myst' reference target not found: 'test' [myst.xref_missing]
<src>/index.md:1: (WARNING/2) 'myst' reference target not found: 'name with spaces' [myst.xref_missing]
.

[implicit_anchor] --myst-heading-anchors=1
.
# Title
# Longer title with **nested** (syntax)
## Non-anchor heading

[](#title)
<project:#longer-title-with-nested-syntax>
[explicit](#title)
.
<document source="<src>/index.md">
    <section ids="title" names="title" slug="title">
        <title>
            Title
    <section ids="longer-title-with-nested-syntax" names="longer\ title\ with\ nested\ (syntax)" slug="longer-title-with-nested-syntax">
        <title>
            Longer title with
            <strong>
                nested
             (syntax)
        <section ids="non-anchor-heading" names="non-anchor\ heading">
            <title>
                Non-anchor heading
            <paragraph>
                <reference id_link="True" refid="title">
                    <inline classes="std std-ref">
                        Title

                <reference id_link="True" refid="longer-title-with-nested-syntax">
                    <inline classes="std std-ref">
                        Longer title with nested (syntax)

                <reference id_link="True" refid="title">
                    explicit
.

[explicit-heading] 
.
(target)=
# Test

[](#target)
<project:#target>
[explicit](#target)
.
<document ids="test target" names="test target" source="<src>/index.md" title="Test">
    <title>
        Test
    <target refid="target">
    <paragraph>
        <reference id_link="True" refid="target">
            <inline classes="std std-ref">
                Test

        <reference id_link="True" refid="target">
            <inline classes="std std-ref">
                Test

        <reference id_link="True" refid="target">
            explicit
.

[explicit>implicit] --myst-heading-anchors=1
.
# Test

(test)=
## Other

[](#test)
.
<document dupnames="test" ids="test" slug="test" source="<src>/index.md" title="Test">
    <title>
        Test
    <subtitle ids="other test-1" names="other test">
        Other
    <system_message backrefs="test-1" level="1" line="3" source="<src>/index.md" type="INFO">
        <paragraph>
            Duplicate implicit target name: "test".
    <target refid="test-1">
    <paragraph>
        <reference id_link="True" refid="test-1">
            <inline classes="std std-ref">
                Other
.

[id-with-spaces] 
.
(name with spaces)=
Paragraph

[](<#name with spaces>)
.
<document source="<src>/index.md">
    <target refid="name-with-spaces">
    <paragraph ids="name-with-spaces" names="name\ with\ spaces">
        Paragraph
    <paragraph>
        <reference id_link="True" refid="name-with-spaces">
            <inline classes="std std-ref">
                #name with spaces
.

[ref-table] 
.
```{table} caption
:name: table
a  | b
-- | --
c  | d
```

[](#table)
<project:#table>
[explicit](#table)
.
<document source="<src>/index.md">
    <table classes="colwidths-auto" ids="table" names="table">
        <title>
            caption
        <tgroup cols="2">
            <colspec colwidth="50">
            <colspec colwidth="50">
            <thead>
                <row>
                    <entry>
                        <paragraph>
                            a
                    <entry>
                        <paragraph>
                            b
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            c
                    <entry>
                        <paragraph>
                            d
    <paragraph>
        <reference id_link="True" refid="table">
            <inline classes="std std-ref">
                caption

        <reference id_link="True" refid="table">
            <inline classes="std std-ref">
                caption

        <reference id_link="True" refid="table">
            explicit
.
