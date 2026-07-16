[resolved] --myst-enable-extensions=section_ref
.
# Title

Intro referencing §1, §1.1 and §2.

## Section One

### Sub One One

## Section Two
.
<document ids="title" names="title" source="<src>/index.md" title="Title">
    <title>
        Title
    <paragraph>
        Intro referencing
        <reference classes="section-ref" internal="True" refid="section-one" reftitle="Section One">
            §1
        ,
        <reference classes="section-ref" internal="True" refid="sub-one-one" reftitle="Sub One One">
            §1.1
         and
        <reference classes="section-ref" internal="True" refid="section-two" reftitle="Section Two">
            §2
        .
    <section ids="section-one" names="section\ one">
        <title>
            Section One
        <section ids="sub-one-one" names="sub\ one\ one">
            <title>
                Sub One One
    <section ids="section-two" names="section\ two">
        <title>
            Section Two
.

[multiple-headings] --myst-enable-extensions=section_ref
.
See §1 and §2.

# First

# Second
.
<document source="<src>/index.md">
    <paragraph>
        See
        <reference classes="section-ref" internal="True" refid="first" reftitle="First">
            §1
         and
        <reference classes="section-ref" internal="True" refid="second" reftitle="Second">
            §2
        .
    <section ids="first" names="first">
        <title>
            First
    <section ids="second" names="second">
        <title>
            Second
.

[forward-reference] --myst-enable-extensions=section_ref
.
# Title

## First

Text in first, see §2.

## Second

Text in second.
.
<document ids="title" names="title" source="<src>/index.md" title="Title">
    <title>
        Title
    <section ids="first" names="first">
        <title>
            First
        <paragraph>
            Text in first, see
            <reference classes="section-ref" internal="True" refid="second" reftitle="Second">
                §2
            .
    <section ids="second" names="second">
        <title>
            Second
        <paragraph>
            Text in second.
.

[unresolved] --myst-enable-extensions=section_ref
.
# Title

See §9.9 which does not exist.

## Only Section
.
<document ids="title" names="title" source="<src>/index.md" title="Title">
    <title>
        Title
    <paragraph>
        See
        <inline classes="section-ref" section_numbers="9 9">
            §9.9
         which does not exist.
    <section ids="only-section" names="only\ section">
        <title>
            Only Section


<src>/index.md:3: (WARNING/2) Section reference target not found: '§9.9' [myst.section_ref]
.

[in-link-text] --myst-enable-extensions=section_ref
.
# Title

## One

## Two

A link [see §1](https://example.com) leaves §1 inert, but body §2 resolves.
.
<document ids="title" names="title" source="<src>/index.md" title="Title">
    <title>
        Title
    <section ids="one" names="one">
        <title>
            One
    <section ids="two" names="two">
        <title>
            Two
        <paragraph>
            A link
            <reference refuri="https://example.com">
                see
                <inline classes="section-ref" section_numbers="1">
                    §1
             leaves
            <reference classes="section-ref" internal="True" refid="one" reftitle="One">
                §1
             inert, but body
            <reference classes="section-ref" internal="True" refid="two" reftitle="Two">
                §2
             resolves.
.

[in-heading] --myst-enable-extensions=section_ref
.
# Title

## Heading with §1 inside

## Other

Body §1 resolves to the first section.
.
<document ids="title" names="title" source="<src>/index.md" title="Title">
    <title>
        Title
    <section ids="heading-with-1-inside" names="heading\ with\ §1\ inside">
        <title>
            Heading with
            <inline classes="section-ref" section_numbers="1">
                §1
             inside
    <section ids="other" names="other">
        <title>
            Other
        <paragraph>
            Body
            <reference classes="section-ref" internal="True" refid="heading-with-1-inside" reftitle="Heading with §1 inside">
                §1
             resolves to the first section.
.
