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
            <reference classes="doc myst-project" internal="True" refuri="other.html">
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
            <reference classes="doc myst-project" internal="True" refuri="other.html">
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
            <reference classes="doc myst-project" internal="True" refuri="other.html">
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
            <reference classes="std-label myst-project" internal="True" refuri="other.html#ref2">
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
            <inline classes="myst-ref-error myst-project">
                xxx

<src>/test.md:2: WARNING: Unmatched target '*:*:xxx' in doc 'other' [myst.xref_missing]
.

empty_fragment
.
# Title
[](#)
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <inline classes="myst-ref-error">

<src>/test.md:2: WARNING: No path or target given for project reference [myst.xref_error]
.

fragment_local
.
(ref)=
# Title
[](.#ref)
.
<document source="root/test.md">
    <target refid="ref">
    <section ids="title ref" names="title ref">
        <title>
            Title
        <paragraph>
            <reference classes="std-label myst-project" internal="True" refid="ref">
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
            <reference classes="std-label myst-project" internal="True" refid="ref">
                Title
.

fragment_same_doc_text
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
            <reference classes="std-label myst-project" internal="True" refid="ref">
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
            <reference classes="std-label myst-project" internal="True" refid="ref">
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
            <reference classes="std-label myst-project" internal="True" refid="ref">
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
            <reference classes="doc myst-project" internal="True" refuri="other.html">
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
            <inline classes="myst-ref-error myst-project">
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
            <reference classes="std-label myst-project" internal="True" refuri="other.html#ref2">
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
            <inline classes="myst-ref-error myst-project">
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
            <reference classes="std-doc myst-project" internal="True" refuri="index.html">
                Main
.

project_auto
.
# Title
<project:#index>
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <reference classes="std-doc myst-project" internal="True" refuri="index.html">
                Main
.

project_auto_missing
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

project_text
.
# Title
[*text*](project:#index)
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <reference classes="std-doc myst-project" internal="True" refuri="index.html">
                <emphasis>
                    text
.

project_missing
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

project_duplicate_local_first
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
            <reference classes="std-label myst-project" internal="True" refid="index">
                text

<src>/test.md:3: WARNING: Multiple targets found for '*:*:index': 'std:label:index','std:doc:index' [myst.xref_duplicate]
.

project_duplicate_non_local
.
# Title
<project:#duplicate>
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <reference classes="std-label myst-project" internal="True" refuri="other.html#duplicate">
                Other

<src>/test.md:2: WARNING: Multiple targets found for '*:*:duplicate': 'std:label:duplicate','std:term:duplicate' [myst.xref_duplicate]
.

project_filter
.
# Title
<project:?*:term#duplicate>
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <reference classes="std-term myst-project" internal="True" refuri="other.html#term-duplicate">
                duplicate
.

myst_project_pattern
.
(target)=
# Title
[](#*get)
.
<document source="root/test.md">
    <target refid="target">
    <section ids="title target" names="title target">
        <title>
            Title
        <paragraph>
            <reference classes="std-label myst-project" internal="True" refid="target">
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
            <reference classes="std-label myst-inv" internal="False" reftitle="(in Python)" refuri="https://project.com/index.html#ref">
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
            <reference classes="std-label myst-inv" internal="False" reftitle="(in Python)" refuri="https://project.com/index.html#ref">
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
            <reference classes="std-label myst-inv" internal="False" reftitle="(in Python)" refuri="https://project.com/index.html#ref">
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
            <reference classes="std-label myst-inv" internal="False" reftitle="(in Python)" refuri="https://project.com/index.html#ref">
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
[*text*](myst:#*modindex)
.
<document source="root/test.md">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            <inline classes="myst-ref-error myst-inv">
                <emphasis>
                    text

<src>/test.md:2: WARNING: Multiple targets found for '*:*:*:*modindex': 'project:std:label:modindex','project:std:label:py-modindex' [myst.iref_duplicate]
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
            <reference classes="myst-anchor myst-project" internal="True" refid="title">
                Title

<src>/test.md:2: WARNING: Link target 'myst:anchor:title' in doc 'test' is auto-generated, so may change unexpectedly [myst.xref_not_explicit]
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

ref_replacements_warning [NUMBERED]
.
# Section

(para)=
paragraph

[{number}](#para)
.
<document source="root/test.md">
    <section ids="section" names="section">
        <title>
            Section
        <target refid="para">
        <paragraph ids="para" names="para">
            paragraph
        <paragraph>
            <reference classes="std-label myst-project" internal="True" refid="para">
                ?

<src>/test.md:6: WARNING: '{number}' replacement is not available [myst.xref_replace]
.

ref_replacements [NUMBERED]
.
(sect)=
# Section
(subsect)=
## Subsection
[*{name}* {number}](#sect)
[*{name}* {number}](#subsect)
.
<document source="root/test.md">
    <target refid="sect">
    <section ids="section sect" names="section sect">
        <title>
            Section
        <target refid="subsect">
        <section ids="subsection subsect" names="subsection subsect">
            <title>
                Subsection
            <paragraph>
                <reference classes="std-label myst-project" internal="True" refid="sect">
                    <emphasis>
                        Section
                     1

                <reference classes="std-label myst-project" internal="True" refid="subsect">
                    <emphasis>
                        Subsection
                     1.1
.

ref_replacements_anchor [NUMBERED] [ADD_ANCHORS]
.
(sect)=
# Section
(subsect)=
## Subsection
[*{name}* {number}](#section)
[*{name}* {number}](#subsection)
.
<document source="root/test.md">
    <target refid="sect">
    <section anchor_id="section" ids="section sect" names="section sect">
        <title>
            Section
        <target refid="subsect">
        <section anchor_id="subsection" ids="subsection subsect" names="subsection subsect">
            <title>
                Subsection
            <paragraph>
                <reference classes="myst-anchor myst-project" internal="True" refid="section">
                    <emphasis>
                        Section
                     1

                <reference classes="myst-anchor myst-project" internal="True" refid="subsection">
                    <emphasis>
                        Subsection
                     1.1

<src>/test.md:5: WARNING: Link target 'myst:anchor:section' in doc 'test' is auto-generated, so may change unexpectedly [myst.xref_not_explicit]
<src>/test.md:5: WARNING: Link target 'myst:anchor:subsection' in doc 'test' is auto-generated, so may change unexpectedly [myst.xref_not_explicit]
.
