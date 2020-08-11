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
