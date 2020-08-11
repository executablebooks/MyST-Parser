--------------------------------
Basic note:
.
::: {note}
*hallo*
:::
.
<document source="notset">
    <note classes="">
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
    <important classes="">
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
    <admonition classes="other">
        <title>
             A 
            <strong>
                title
        <paragraph>
            <emphasis>
                hallo
.
