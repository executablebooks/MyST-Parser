Duplicate Reference definitions:
.
[a]: b
[a]: c
.
<string>:2: (WARNING/2) Duplicate reference definition: A [myst.duplicate_def]
.

Missing Reference:
.
[a](b)
.
<string>:1: (ERROR/3) Unknown target name: "b".
.

Unknown role:
.
abc

{xyz}`a`
.
<string>:3: (WARNING/2) Unknown interpreted text role "xyz". [myst.role_unknown]
.

Unknown directive:
.

```{xyz}
```
.
<string>:2: (WARNING/2) Unknown directive type: 'xyz' [myst.directive_unknown]
.

Bad Front Matter:
.
---
a: {
---
.
<string>:1: (WARNING/2) Malformed YAML [myst.topmatter]
.

Unknown Front Matter myst key:
.
---
myst:
  unknown: true
---
.
<string>:1: (WARNING/2) Unknown field: unknown [myst.topmatter]
.

Invalid Front Matter myst key:
.
---
myst:
  title_to_header: 1
  url_schemes: [1]
  substitutions:
    key: []
---
.
<string>:1: (WARNING/2) 'title_to_header' must be of type <class 'bool'> (got 1 that is a <class 'int'>). [myst.topmatter]
<string>:1: (WARNING/2) 'url_schemes' is not a list of strings: [1] [myst.topmatter]
.

Bad HTML Meta
.
---
myst:
  html_meta:
    name noequals: value

---
.
<string>:: (ERROR/3) Error parsing meta tag attribute "name noequals": no '=' in noequals.
.

Directive parsing error:
.

```{class}
```
.
<string>:2: (ERROR/3) Directive 'class': 1 argument(s) required, 0 supplied
.

Directive run error:
.

```{date}
x
```
.
<string>:2: (ERROR/3) Invalid context: the "date" directive can only be used within a substitution definition.
.

Do not start headings at H1:
.
## title 1
.
<string>:1: (WARNING/2) Document headings start at H2, not H1 [myst.header]
.

Non-consecutive headings:
.
# title 1
### title 3
.
<string>:2: (WARNING/2) Non-consecutive header level increase; H1 to H3 [myst.header]
.

multiple footnote definitions
.
[^a]

[^a]: definition 1
[^a]: definition 2
.
<string>:: (WARNING/2) Multiple footnote definitions found for label: 'a' [myst.footnote]
.

Warnings in eval-rst
.
some external

lines

```{eval-rst}
some internal

lines

.. unknown:: some text

:unknown:`a`
```
.
<string>:10: (ERROR/3) Unknown directive type "unknown".

.. unknown:: some text

<string>:12: (ERROR/3) Unknown interpreted text role "unknown".
.

bad-option-value
.
```{note}
:class: [1]
```
.
<string>:1: (WARNING/2) 'note': option "class" value not string (enclose with ""): [1] [myst.directive_parse]
<string>:1: (ERROR/3) Content block expected for the "note" directive; none found.
.

header nested in admonition
.
```{note}
# Header
```
.

.

nested parse warning
.
Paragraph

```{note}
:class: abc
:name: xyz

{unknown}`a`
```
.
<string>:7: (WARNING/2) Unknown interpreted text role "unknown". [myst.role_unknown]
.
