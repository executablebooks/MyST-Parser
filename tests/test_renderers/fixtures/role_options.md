Test Role 1:
.
```{restructuredtext-test-directive}
```
.
<document source="notset">
    <system_message level="1" line="1" source="notset" type="INFO">
        <paragraph>
            Directive processed. Type="restructuredtext-test-directive", arguments=[], options={}, content: None
.

-----------------------------
Test Role 2:
.
```{restructuredtext-test-directive}
foo
```
.
<document source="notset">
    <system_message level="1" line="1" source="notset" type="INFO">
        <paragraph>
            Directive processed. Type="restructuredtext-test-directive", arguments=[], options={}, content:
        <literal_block xml:space="preserve">
            foo
.

-----------------------------
Test Role 3:
.
```{restructuredtext-test-directive} foo
```
.
<document source="notset">
    <system_message level="1" line="1" source="notset" type="INFO">
        <paragraph>
            Directive processed. Type="restructuredtext-test-directive", arguments=['foo'], options={}, content: None
.

-----------------------------
Test Role 4:
.
```{restructuredtext-test-directive} foo
bar
```
.
<document source="notset">
    <system_message level="1" line="1" source="notset" type="INFO">
        <paragraph>
            Directive processed. Type="restructuredtext-test-directive", arguments=['foo'], options={}, content:
        <literal_block xml:space="preserve">
            bar
.

-----------------------------
Test Role 5:
.
```{restructuredtext-test-directive} foo bar
```
.
<document source="notset">
    <system_message level="1" line="1" source="notset" type="INFO">
        <paragraph>
            Directive processed. Type="restructuredtext-test-directive", arguments=['foo bar'], options={}, content: None
.

-----------------------------
Test Role 6:
.
```{restructuredtext-test-directive} foo bar
baz
```
.
<document source="notset">
    <system_message level="1" line="1" source="notset" type="INFO">
        <paragraph>
            Directive processed. Type="restructuredtext-test-directive", arguments=['foo bar'], options={}, content:
        <literal_block xml:space="preserve">
            baz
.

-----------------------------
Test Role 7:
.
```{restructuredtext-test-directive}

foo
```
.
<document source="notset">
    <system_message level="1" line="1" source="notset" type="INFO">
        <paragraph>
            Directive processed. Type="restructuredtext-test-directive", arguments=[], options={}, content:
        <literal_block xml:space="preserve">
            foo
.

-----------------------------
Test Role Options 1:
.
```{restructuredtext-test-directive}
---
option1: a
option2: b
---
foo
```
.
<document source="notset">
    <system_message level="1" line="1" source="notset" type="INFO">
        <paragraph>
            Directive processed. Type="restructuredtext-test-directive", arguments=[], options={'option1': 'a', 'option2': 'b'}, content:
        <literal_block xml:space="preserve">
            foo
.

-----------------------------
Test Role Options 2:
.
```{restructuredtext-test-directive}
:option1: a
:option2: b
foo
```
.
<document source="notset">
    <system_message level="1" line="1" source="notset" type="INFO">
        <paragraph>
            Directive processed. Type="restructuredtext-test-directive", arguments=[], options={'option1': 'a', 'option2': 'b'}, content:
        <literal_block xml:space="preserve">
            foo
.

-----------------------------
Test Role Options Error:
.
```{restructuredtext-test-directive}
:option1
:option2: b
foo
```
.
<document source="notset">
    <system_message level="3" line="1" source="notset" type="ERROR">
        <paragraph>
            Directive 'restructuredtext-test-directive':
            Invalid options YAML: mapping values are not allowed here
              in "<unicode string>", line 2, column 8:
                option2: b
                       ^
        <literal_block xml:space="preserve">
            :option1
            :option2: b
            foo
.
