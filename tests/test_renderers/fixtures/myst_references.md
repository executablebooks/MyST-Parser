path_link_implicit_text
.
# Title
[](other.txt)
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <download_reference classes="myst-file" filename="8b15c0404e301d2ad766e86e4f4e1ffd/other.txt" refdoc="test" reftarget="/other.txt">
                <literal>
                    /other.txt
.

path_link_explicit_text
.
# Title
[*text*](other.txt)
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <download_reference classes="myst-file" filename="8b15c0404e301d2ad766e86e4f4e1ffd/other.txt" refdoc="test" reftarget="/other.txt">
                <emphasis>
                    text
.

path_auto
.
# Title
<path:other.txt>
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <download_reference classes="myst-file" filename="8b15c0404e301d2ad766e86e4f4e1ffd/other.txt" refdoc="test" reftarget="other.txt">
                path:other.txt
.

doc_path_relative
.
# Title
[](./other.md)
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <reference classes="myst-doc" internal="True" refuri="other.html">
                Other
.

doc_path_absolute
.
# Title
[](/other.md)
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <reference classes="myst-doc" internal="True" refuri="other.html">
                Other
.

doc_path_text
.
# Title
[*text*](other.md)
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <reference classes="myst-doc" internal="True" refuri="other.html">
                <emphasis>
                    text
.

doc_path_unknown
.
# Title
[*text*](xxx.md)
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <inline classes="myst-ref-error myst-project">
                <emphasis>
                    text

<src>/test.md:2: WARNING: Unknown link URI (implicitly prepending with '#'): 'xxx.md' [myst.invalid_uri]
<src>/test.md:2: WARNING: Unmatched target '*:*:xxx.md' [myst.xref_missing]
.

doc_path_target
.
# Title
[](other.md#ref2)
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <reference classes="myst-doc" internal="True" refuri="other.html#ref2">
                Other
.

doc_path_target_unknown
.
# Title
[](other.md#xxx)
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <inline classes="myst-ref-error myst-doc">
                xxx

<src>/test.md:2: WARNING: Unmatched target '*:*:xxx' in doc 'other' [myst.xref_missing]
.

fragment_local
.
(ref)=
# Title
[](_#ref)
.
<document source="root/test.md">
    <target refid="ref">
    <section ids="title ref" names="title ref">
        <title>
            Title
        <paragraph>
            <reference classes="myst-project" internal="True" refid="ref" reftitle="std:label:ref">
                Title
.

fragment_same_doc
.
(ref)=
# Title
[](#ref)
.
<document source="root/test.md">
    <target refid="ref">
    <section ids="title ref" names="title ref">
        <title>
            Title
        <paragraph>
            <reference classes="myst-project" internal="True" refid="ref" reftitle="std:label:ref">
                Title
.

fragment_same_doc_text_x
.
(ref)=
# Title
[*text*](#ref)
.
<document source="root/test.md">
    <target refid="ref">
    <section ids="title ref" names="title ref">
        <title>
            Title
        <paragraph>
            <reference classes="myst-project" internal="True" refid="ref" reftitle="std:label:ref">
                <emphasis>
                    text
.

project_fragment_local
.
(ref)=
# Title
<project:#ref>
.
<document source="root/test.md">
    <target refid="ref">
    <section ids="title ref" names="title ref">
        <title>
            Title
        <paragraph>
            <reference classes="myst-project" internal="True" refid="ref" reftitle="std:label:ref">
                Title
.

project_fragment_unknown
.
# Title
<project:#a%20b>
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <inline classes="myst-ref-error myst-project">
                project:#a b

<src>/test.md:2: WARNING: Unmatched target '*:*:a b' [myst.xref_missing]
.

project_fragment_local_text
.
(ref)=
# Title
[*text*](project:#ref)
.
<document source="root/test.md">
    <target refid="ref">
    <section ids="title ref" names="title ref">
        <title>
            Title
        <paragraph>
            <reference classes="myst-project" internal="True" refid="ref" reftitle="std:label:ref">
                <emphasis>
                    text
.

project_doc
.
# Title
<project:other.md>
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <reference classes="myst-doc" internal="True" refuri="other.html">
                Other
.

project_doc_no_suffix
.
# Title
<project:other>
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <inline classes="myst-ref-error">
                project:other

<src>/test.md:2: WARNING: Path does not have a known document suffix: other [myst.xref_error]
.

project_doc_missing
.
# Title
<project:xxx.md>
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <inline classes="myst-ref-error myst-doc">
                project:xxx.md

<src>/test.md:2: WARNING: Unknown reference docname 'xxx' [myst.xref_missing]
.

project_doc_target
.
# Title
<project:other.md#ref2>
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <reference classes="myst-doc" internal="True" refuri="other.html#ref2">
                Other
.

project_doc_target_missing
.
# Title
<project:other.md#xxx>
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <inline classes="myst-ref-error myst-doc">
                project:other.md#xxx

<src>/test.md:2: WARNING: Unmatched target '*:*:xxx' in doc 'other' [myst.xref_missing]
.

project_target
.
# Title
[](project:#index)
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <reference classes="myst-project" internal="True" reftitle="myst:project:std:doc" refuri="index.html">
                Main
.

myst_project_auto
.
# Title
<project:#index>
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <reference classes="myst-project" internal="True" reftitle="myst:project:std:doc" refuri="index.html">
                Main
.

myst_project_auto_missing
.
# Title
<project:#xxx>
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <inline classes="myst-ref-error myst-project">
                project:#xxx

<src>/test.md:2: WARNING: Unmatched target '*:*:xxx' [myst.xref_missing]
.

myst_project_text
.
# Title
[*text*](project:#index)
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <reference classes="myst-project" internal="True" reftitle="myst:project:std:doc" refuri="index.html">
                <emphasis>
                    text
.

myst_project_missing
.
# Title
[*text*](project:#xxx)
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <inline classes="myst-ref-error myst-project">
                <emphasis>
                    text

<src>/test.md:2: WARNING: Unmatched target '*:*:xxx' [myst.xref_missing]
.

myst_project_duplicate_local_first
.
(index)=
# Title
[text](project:#index)
.
<document source="root/test.md">
    <target refid="index">
    <section ids="title index" names="title index">
        <title>
            Title
        <paragraph>
            <reference classes="myst-project" internal="True" refid="index" reftitle="std:label:index">
                text
.

project_label
.
(index)=
# Title
[](project:?o=label#index)
.
<document source="root/test.md">
    <target refid="index">
    <section ids="title index" names="title index">
        <title>
            Title
        <paragraph>
            <reference classes="myst-project" internal="True" refid="index" reftitle="std:label:index">
                Title
.

myst_project_pattern
.
(target)=
# Title
[](project:?pat#*get)
.
<document source="root/test.md">
    <target refid="target">
    <section ids="title target" names="title target">
        <title>
            Title
        <paragraph>
            <reference classes="myst-project" internal="True" refid="target" reftitle="std:label:target">
                Title
.

myst_inv [LOAD_INV]
.
# Title
[](myst:#ref)
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <reference classes="inv-project-std-label myst-inv" internal="False" reftitle="(in Python)" refuri="https://project.com/index.html#ref">
                Title
.

myst_inv_auto [LOAD_INV]
.
# Title
<myst:#ref>
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <reference classes="inv-project-std-label myst-inv" internal="False" reftitle="(in Python)" refuri="https://project.com/index.html#ref">
                Title
.

myst_inv_text [LOAD_INV]
.
# Title
[*text*](myst:#ref)
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <reference classes="inv-project-std-label myst-inv" internal="False" reftitle="(in Python)" refuri="https://project.com/index.html#ref">
                <emphasis>
                    text
.

myst_inv_named [LOAD_INV]
.
# Title
<myst:project#ref>
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <reference classes="inv-project-std-label myst-inv" internal="False" reftitle="(in Python)" refuri="https://project.com/index.html#ref">
                Title
.

myst_inv_missing_name [LOAD_INV]
.
# Title
<myst:xxx#ref>
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <inline classes="myst-ref-error myst-inv">
                myst:xxx#ref

<src>/test.md:2: WARNING: Unknown inventory 'xxx' [myst.iref_missing]
.

myst_inv_missing_target [LOAD_INV]
.
# Title
[*text*](myst:#xxx)
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <inline classes="myst-ref-error myst-inv">
                <emphasis>
                    text

<src>/test.md:2: WARNING: Unmatched target '*:*:*:xxx' [myst.iref_missing]
.

myst_inv_duplicate [LOAD_INV]
.
# Title
[*text*](myst:?pat#*modindex)
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <inline classes="myst-ref-error myst-inv">
                <emphasis>
                    text

<src>/test.md:2: WARNING: Multiple matches found for target '*:*:*:*modindex': 'project:std:label:modindex','project:std:label:py-modindex' [myst.iref_duplicate]
.

implicit_anchors [ADD_ANCHORS]
.
# Title
[](#title)
.
<document source="root/test.md">
    <section anchor_id="title" ids="title" names="title">
        <title>
            Title
        <paragraph>
            <reference classes="myst-project" internal="True" refid="title" reftitle="myst:anchor:title">
                Title

<src>/test.md:2: WARNING: Local link target 'myst:anchor:title' is auto-generated, so may change unexpectedly [myst.xref_not_explicit]
.

deprecated
.
# Title
[](ref)
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <inline classes="myst-ref-error myst-project">
                ref

<src>/test.md:2: WARNING: Unknown link URI (implicitly prepending with '#'): 'ref' [myst.invalid_uri]
<src>/test.md:2: WARNING: Unmatched target '*:*:ref' [myst.xref_missing]
.
