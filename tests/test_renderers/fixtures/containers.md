Basic note:
.
::: {note}
*hallo*
:::
.
<document source="<src>/index.md">
    <note>
        <paragraph>
            <emphasis>
                hallo
.

Admonition with options:
.
::: {admonition} A **title**
:class: other

*hallo*
:::
.
<document source="<src>/index.md">
    <admonition classes="other">
        <title>
            A
            <strong>
                title
        <paragraph>
            <emphasis>
                hallo
.

empty name:
.
:::
This is **content**
:::
.
<document source="<src>/index.md">
    <container is_div="True">
        <paragraph>
            This is
            <strong>
                content
.

has name:
.
:::name
This is **content**
:::
.
<document source="<src>/index.md">
    <container classes="name" is_div="True">
        <paragraph>
            This is
            <strong>
                content
.
