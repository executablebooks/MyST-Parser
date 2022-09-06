unhandled
.
# Title
[](ref)
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <reference refuri="ref">

<src>/test.md:2: WARNING: Unhandled link URI (prepend with '#' or 'myst:project#'?): 'ref' [myst.invalid_uri]
.

doc_path
.
# Title
[](other.md)
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

file_path
.
# Title
[](other.txt)
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <download_reference classes="myst" filename="8b15c0404e301d2ad766e86e4f4e1ffd/other.txt" refdoc="test" reftarget="other.txt">
                <literal classes="xref download">
                    other.txt
.

file_path_text
.
# Title
[*text*](other.txt)
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <download_reference classes="myst" filename="8b15c0404e301d2ad766e86e4f4e1ffd/other.txt" refdoc="test" reftarget="other.txt">
                <inline classes="xref download">
                    <emphasis>
                        text
.

fragment_local
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
            <reference classes="myst-local" internal="True" refid="ref">
                Title
.

fragment_local_text
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
            <reference classes="myst-local" internal="True" refid="ref">
                <emphasis>
                    text
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

myst_local
.
(ref)=
# Title
[](myst:local#ref)
.
<document source="root/test.md">
    <target refid="ref">
    <section ids="title ref" names="title ref">
        <title>
            Title
        <paragraph>
            <reference classes="myst-local" internal="True" refid="ref">
                Title
.

myst_local_auto
.
(ref)=
# Title
<myst:local#ref>
.
<document source="root/test.md">
    <target refid="ref">
    <section ids="title ref" names="title ref">
        <title>
            Title
        <paragraph>
            <reference classes="myst-local" internal="True" refid="ref">
                Title
.

myst_local_auto_encode
.
# Title
<myst:local#a%20b>
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <reference classes="myst-local" refuri="#a b">
                myst:local#a b

<src>/test.md:2: WARNING: ref name does not match any known target: 'a b' [myst.ref_missing]
.

myst_local_text
.
(ref)=
# Title
[*text*](myst:local#ref)
.
<document source="root/test.md">
    <target refid="ref">
    <section ids="title ref" names="title ref">
        <title>
            Title
        <paragraph>
            <reference classes="myst-local" internal="True" refid="ref">
                <emphasis>
                    text
.

myst_doc
.
# Title
<myst:doc#other>
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <reference classes="myst-doc" internal="True" refuri="other.html">
                Other
.

myst_doc_missing
.
# Title
<myst:doc#xxx>
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <inline classes="myst-ref-error myst-doc">
                myst:doc#xxx

<src>/test.md:2: WARNING: Unknown reference docname 'xxx' [myst.xref_missing]
.

myst_doc_target
.
# Title
<myst:doc?t=ref2#other>
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <reference classes="myst-doc" internal="True" refuri="other.html#ref2">
                Other
.

myst_doc_target_missing
.
# Title
<myst:doc?t=xxx#other>
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <inline classes="myst-ref-error myst-doc">
                myst:doc?t=xxx#other

<src>/test.md:2: WARNING: Unknown ref 'xxx' in doc 'other' [myst.xref_missing]
.

myst_project
.
# Title
[](myst:project#index)
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
<myst:project#index>
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
<myst:project#xxx>
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <inline classes="myst-ref-error myst-project">
                myst:project#xxx

<src>/test.md:2: WARNING: Unmatched target 'local:?:?:xxx' [myst.xref_missing]
.

myst_project_text
.
# Title
[*text*](myst:project#index)
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
[*text*](myst:project#xxx)
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <inline classes="myst-ref-error myst-project">
                <emphasis>
                    text

<src>/test.md:2: WARNING: Unmatched target 'local:?:?:xxx' [myst.xref_missing]
.

myst_project_duplicate
.
(index)=
# Title
[text](myst:project#index)
.
<document source="root/test.md">
    <target refid="index">
    <section ids="title index" names="title index">
        <title>
            Title
        <paragraph>
            <inline classes="myst-ref-error myst-project">
                text

<src>/test.md:3: WARNING: Multiple matches found for target 'local:?:?:index' in 'local:std:label:index','local:std:doc:index' [myst.xref_duplicate]
.

myst_project_label
.
(index)=
# Title
[](myst:project?o=label#index)
.
<document source="root/test.md">
    <target refid="index">
    <section ids="title index" names="title index">
        <title>
            Title
        <paragraph>
            <reference classes="myst-project" internal="True" refid="index" reftitle="myst:project:std:label">
                Title
.

myst_project_pattern
.
(target)=
# Title
[](myst:project?pat#*get)
.
<document source="root/test.md">
    <target refid="target">
    <section ids="title target" names="title target">
        <title>
            Title
        <paragraph>
            <reference classes="myst-project" internal="True" refid="target" reftitle="myst:project:std:label">
                Title
.

myst_inv [LOAD_INV]
.
# Title
[](myst:inv#ref)
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
<myst:inv#ref>
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
[*text*](myst:inv#ref)
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

myst_inv_missing [LOAD_INV]
.
# Title
[*text*](myst:inv#xxx)
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <inline classes="myst-ref-error myst-inv">
                <emphasis>
                    text

<src>/test.md:2: WARNING: Unmatched target '?:?:?:xxx' [myst.iref_missing]
.

myst_inv_duplicate [LOAD_INV]
.
# Title
[*text*](myst:inv?pat#*modindex)
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <inline classes="myst-ref-error myst-inv">
                <emphasis>
                    text

<src>/test.md:2: WARNING: Multiple matches found for target '?:?:?:*modindex' in 'project:std:label:modindex','project:std:label:py-modindex' [myst.iref_duplicate]
.
