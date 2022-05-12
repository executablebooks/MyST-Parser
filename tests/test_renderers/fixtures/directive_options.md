Test Directive 1:
.
```{restructuredtext-test-directive}
```
.
<document source="<src>/index.md">
    <system_message level="1" line="1" source="<src>/index.md" type="INFO">
        <paragraph>
            Directive processed. Type="restructuredtext-test-directive", arguments=[], options={}, content: None
.

Test Directive 2:
.
```{restructuredtext-test-directive}
foo
```
.
<document source="<src>/index.md">
    <system_message level="1" line="1" source="<src>/index.md" type="INFO">
        <paragraph>
            Directive processed. Type="restructuredtext-test-directive", arguments=[], options={}, content:
        <literal_block xml:space="preserve">
            foo
.

Test Directive 3:
.
```{restructuredtext-test-directive} foo
```
.
<document source="<src>/index.md">
    <system_message level="1" line="1" source="<src>/index.md" type="INFO">
        <paragraph>
            Directive processed. Type="restructuredtext-test-directive", arguments=['foo'], options={}, content: None
.

Test Directive 4:
.
```{restructuredtext-test-directive} foo
bar
```
.
<document source="<src>/index.md">
    <system_message level="1" line="1" source="<src>/index.md" type="INFO">
        <paragraph>
            Directive processed. Type="restructuredtext-test-directive", arguments=['foo'], options={}, content:
        <literal_block xml:space="preserve">
            bar
.

Test Directive 5:
.
```{restructuredtext-test-directive} foo bar
```
.
<document source="<src>/index.md">
    <system_message level="1" line="1" source="<src>/index.md" type="INFO">
        <paragraph>
            Directive processed. Type="restructuredtext-test-directive", arguments=['foo bar'], options={}, content: None
.

Test Directive 6:
.
```{restructuredtext-test-directive} foo bar
baz
```
.
<document source="<src>/index.md">
    <system_message level="1" line="1" source="<src>/index.md" type="INFO">
        <paragraph>
            Directive processed. Type="restructuredtext-test-directive", arguments=['foo bar'], options={}, content:
        <literal_block xml:space="preserve">
            baz
.

Test Directive 7:
.
```{restructuredtext-test-directive}

foo
```
.
<document source="<src>/index.md">
    <system_message level="1" line="1" source="<src>/index.md" type="INFO">
        <paragraph>
            Directive processed. Type="restructuredtext-test-directive", arguments=[], options={}, content:
        <literal_block xml:space="preserve">
            foo
.

Test Directive Options 1:
.
```{restructuredtext-test-directive}
---
option1: a
option2: b
---
foo
```
.
<document source="<src>/index.md">
    <system_message level="1" line="1" source="<src>/index.md" type="INFO">
        <paragraph>
            Directive processed. Type="restructuredtext-test-directive", arguments=[], options={'option1': 'a', 'option2': 'b'}, content:
        <literal_block xml:space="preserve">
            foo
.

Test Directive Options 2:
.
```{restructuredtext-test-directive}
:option1: a
:option2: b
foo
```
.
<document source="<src>/index.md">
    <system_message level="1" line="1" source="<src>/index.md" type="INFO">
        <paragraph>
            Directive processed. Type="restructuredtext-test-directive", arguments=[], options={'option1': 'a', 'option2': 'b'}, content:
        <literal_block xml:space="preserve">
            foo
.

Test Directive Options Error:
.
```{restructuredtext-test-directive}
:option1
:option2: b
foo
```
.
<document source="<src>/index.md">
    <system_message level="3" line="1" source="<src>/index.md" type="ERROR">
        <paragraph>
            Directive 'restructuredtext-test-directive': Invalid options YAML: mapping values are not allowed here
              in "<unicode string>", line 2, column 8:
                option2: b
                       ^
        <literal_block xml:space="preserve">
            :option1
            :option2: b
            foo
.

Unknown Directive:
.
```{unknown}
```
.
<document source="<src>/index.md">
    <system_message level="3" line="1" source="<src>/index.md" type="ERROR">
        <paragraph>
            Unknown directive type "unknown".
    <system_message level="1" line="1" source="<src>/index.md" type="INFO">
        <paragraph>
            No directive entry for "unknown" in module "docutils.parsers.rst.languages.en".
            Trying "unknown" as canonical directive name.
.
