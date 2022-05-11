Simple:
.
Term **1**

: Definition *1*

  second paragraph

Term 2
  ~ Definition 2a
  ~ Definition 2b

Term 3
  :     code block

  : > quote

  : other
.
<document source="<src>/index.md">
    <definition_list classes="simple myst">
        <definition_list_item>
            <term>
                Term
                <strong>
                    1
            <definition>
                <paragraph>
                    Definition
                    <emphasis>
                        1
                <paragraph>
                    second paragraph
        <definition_list_item>
            <term>
                Term 2
            <definition>
                <paragraph>
                    Definition 2a
            <definition>
                <paragraph>
                    Definition 2b
        <definition_list_item>
            <term>
                Term 3
            <definition>
                <literal_block language="none" xml:space="preserve">
                    code block
            <definition>
                <block_quote>
                    <paragraph>
                        quote
            <definition>
                <paragraph>
                    other
.
