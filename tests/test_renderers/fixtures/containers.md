--------------------------------
Basic note:
.
::: {note}
*hallo*
:::
.
<document source="notset">
    <note>
        <paragraph>
            <emphasis>
                hallo
.

--------------------------------
Nested notes:
.
:::: {important}
::: {note,other}
*hallo*
:::
::::
.
<document source="notset">
    <important>
        <system_message level="2" line="1" source="notset" type="WARNING">
            <paragraph>
                comma-separated classes are deprecated, use `:class:` option instead
        <note classes="other">
            <paragraph>
                <emphasis>
                    hallo
.

--------------------------------
Admonition with title:
.
::: {admonition,other} A **title**
*hallo*
:::
.
<document source="notset">
    <system_message level="2" line="1" source="notset" type="WARNING">
        <paragraph>
            comma-separated classes are deprecated, use `:class:` option instead
    <admonition classes="other">
        <title>
            A 
            <strong>
                title
        <paragraph>
            <emphasis>
                hallo
.

--------------------------------
Admonition with options:
.
::: {admonition} A **title**
:class: other

*hallo*
:::
.
<document source="notset">
    <admonition classes="other">
        <title>
            A 
            <strong>
                title
        <paragraph>
            <emphasis>
                hallo
.
