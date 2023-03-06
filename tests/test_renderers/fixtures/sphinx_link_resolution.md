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
.
<document source="<src>/index.md">
    <paragraph>
        <pending_xref refdoc="index" refdomain="True" refexplicit="False" reftarget="test" reftype="myst">
            <inline classes="xref myst">

        <pending_xref refdoc="index" refdomain="True" refexplicit="False" reftarget="test" reftype="myst">
            <inline classes="xref myst">

        <pending_xref refdoc="index" refdomain="True" refexplicit="True" reftarget="test" reftype="myst">
            <inline classes="xref myst">
                explicit
.

[implicit_anchor] {"myst_heading_anchors": 1}
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
[](<#name with spaces>)
.
<document source="<src>/index.md">
    <target refid="target">
    <section ids="test target" names="test target">
        <title>
            Test
        <paragraph>
            <reference id_link="True" refid="target">
                <inline classes="std std-ref">
                    Test

            <reference id_link="True" refid="target">
                <inline classes="std std-ref">
                    Test

            <reference id_link="True" refid="target">
                explicit

            <pending_xref refdoc="index" refdomain="True" refexplicit="False" reftarget="name with spaces" reftype="myst">
                <inline classes="xref myst">
.

[explicit>implicit] {"myst_heading_anchors": 1}
.
# Test

(test)=
## Other

[](#test)
.
<document source="<src>/index.md">
    <section dupnames="test" ids="test" slug="test">
        <title>
            Test
        <target refid="id1">
        <section ids="other id1" names="other test">
            <title>
                Other
            <paragraph>
                <reference id_link="True" refid="id1">
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

[external-file] 
.
[](test.txt)
<path:./test.txt>
[relative to source dir](/test.txt)
.
<document source="<src>/index.md">
    <paragraph>
        <download_reference filename="dd18bf3a8e0a2a3e53e2661c7fb53534/test.txt" refdoc="index" refdomain="True" refexplicit="False" reftarget="test.txt" reftype="myst">
            <literal classes="xref download myst">
                test.txt

        <download_reference filename="dd18bf3a8e0a2a3e53e2661c7fb53534/test.txt" refdoc="index" refdomain="True" refexplicit="False" reftarget="./test.txt" reftype="myst">
            <literal classes="xref download myst">
                ./test.txt

        <download_reference filename="dd18bf3a8e0a2a3e53e2661c7fb53534/test.txt" refdoc="index" refdomain="True" refexplicit="True" reftarget="/test.txt" reftype="myst">
            <inline classes="xref download myst">
                relative to source dir
.

[source-file] 
.
[](other.rst)
<project:other.rst>
[relative to source dir](/other.rst)
.
<document source="<src>/index.md">
    <paragraph>
        <pending_xref refdoc="index" refdomain="doc" refexplicit="False" reftarget="other" reftargetid="True" reftype="myst">
            <inline classes="xref myst">

        <pending_xref refdoc="index" refdomain="doc" refexplicit="False" reftarget="other" reftargetid="True" reftype="myst">
            <inline classes="xref myst">

        <pending_xref refdoc="index" refdomain="doc" refexplicit="True" reftarget="other" reftargetid="True" reftype="myst">
            <inline classes="xref myst">
                relative to source dir
.
