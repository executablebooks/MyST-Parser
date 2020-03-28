Basic Include:
.
```{include} other.md
```
.
<document source="tmpdir/test.md">
    <paragraph>
        a
        
        b
        
        c
.

Include with Front Matter (should be ignored):
.
```{include} fmatter.md
```
.
<document source="tmpdir/test.md">
    <paragraph>
        b
.

Include Literal:
.
```{include} other.md
:literal: True
```
.
<document source="tmpdir/test.md">
    <literal_block source="tmpdir/other.md" xml:space="preserve">
        a
        b
        c
.

Include Literal, line range:
.
```{include} other.md
:literal: True
:start-line: 1
:end-line: 2
```
.
<document source="tmpdir/test.md">
    <literal_block source="tmpdir/other.md" xml:space="preserve">
        b
.

Include code:
.
```{include} other.md
:code: md
```
.
<document source="tmpdir/test.md">
    <literal_block classes="code md" source="tmpdir/other.md" xml:space="preserve">
        a
        b
        c
.
