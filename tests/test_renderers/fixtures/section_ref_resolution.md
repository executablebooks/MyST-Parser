The conformance contract for `section_ref` resolution (docs/syntax/optional.md, "Numbering rules"), run through docutils and Sphinx; text that is not a reference (`§0000000001`) has no line.
Each case is a document, then one line per reference in document order after inclusion: `§n -> <target section title>`, plus ` [k]` if k-th of several sections with that title, plus ` @<id>` if the target has a `(label)=`; `§n unresolved` (one warning); or `§n inert` (no link, no warning).
A `-- file: <name>` line starts an extra file; `[id] key=value` options set config for both engines, `docutils:`/`sphinx:` ones for one (`sphinx:extensions` is a comma list added to Sphinx's), and `sphinx-only` cases need a Sphinx-only directive ({only}, {ifconfig}) or a cross-document link.

[C1-title-and-sections]
.
# T

See §1 §1.1 §1.2 §2 §2.1 §3.

## A

### A1

### A2

## B

### B1
.
§1 -> A
§1.1 -> A1
§1.2 -> A2
§2 -> B
§2.1 -> B1
§3 unresolved
.

[C2-title-and-one-section]
.
# T

See §1 and §1.1.

## A

### A1
.
§1 -> A
§1.1 -> A1
.

[C3-subtitle]
.
# T

## A

See §1 and §1.1.

### B
.
§1 -> A
§1.1 -> B
.

[C3-subtitle-only]
.
# T

## A

See §1, not §2.
.
§1 -> A
§2 unresolved
.

[C4-several-top-level]
.
See §1 §1.1 §2 §2.1.

# X

## X1

# Y

## Y1
.
§1 -> X
§1.1 -> X1
§2 -> Y
§2.1 -> Y1
.

[C5-no-h1]
.
## A

### A1

## B

See §1 §1.1 §2.
.
§1 -> A
§1.1 -> A1
§2 -> B
.

[C6-single-root-below-h1]
.
## A

See §1 §2 §1.1 §1.2.

### A1

### A2
.
§1 -> A1
§2 -> A2
§1.1 unresolved
§1.2 unresolved
.

[C7-numbers-as-written]
.
# T

## A

### A1

§0 §01 §1 §01.01 §1.0 §1.1.1.1 §99 §2.1

§000000001 §0000000001 §123456789 §1.1234567890 §1.000000001
.
§0 unresolved
§01 -> A
§1 -> A
§01.01 -> A1
§1.0 unresolved
§1.1.1.1 unresolved
§99 unresolved
§2.1 unresolved
§000000001 -> A
§123456789 unresolved
§1.000000001 -> A1
.

[C8-rubric-and-eval-rst]
.
# T

## A

```{note}
## In a note §1
```

## B

```{eval-rst}
RST section
-----------

text
```

## C

See §1 §1.1 §2 §2.1 §3 §4.
.
§1 -> A
§1 -> A
§1.1 unresolved
§2 -> B
§2.1 -> RST section
§3 -> C
§4 unresolved
.

[C9-include]
.
# T

## A

```{include} part.md
```

## Z

See §1 §2 §2.1 §3.
-- file: part.md
## P

In the included file: §1 §2 §2.1 §9.

### P1
.
§1 -> A
§2 -> P
§2.1 -> P1
§9 unresolved
§1 -> A
§2 -> P
§2.1 -> P1
§3 -> Z
.

[C9-include-heading-offset]
.
# T

## A

```{include} part.md
:heading-offset: 1
```

## Z

See §1 §2 §2.1 §3 §4.
-- file: part.md
# P

## P1
.
§1 -> A
§2 -> P
§2.1 -> P1
§3 -> Z
§4 unresolved
.

[C13-inert-contexts]
.
# T §9

## A §1

## B §9

[link §1](#b), [link §9](https://example.com), *§1*, **§2** and §3.
.
§9 inert
§1 inert
§9 inert
§1 inert
§9 inert
§1 -> A §1
§2 -> B §9
§3 unresolved
.

[C13-reference-in-subtitle]
.
# T

## A §1

See §1 and §1.1.

### B
.
§1 inert
§1 -> A §1
§1.1 -> B
.

[C13-reference-in-anchor-link]
.
# T

## A

[see §1](#a)
.
§1 inert
.

[C13-reference-in-document-link] sphinx-only
.
# T

## A

[see §1](other.md)
.
§1 inert
.

[C13-reference-in-admonition-title]
.
# T

## A

```{admonition} See §1
x
```
.
§1 -> A
.

[C14-duplicate-titles]
.
# T

(lbl)=
## A

## A

## A

See §1 §2 §3.
.
§1 -> A [1] @lbl
§2 -> A [2]
§3 -> A [3]
.

[C14-explicit-target]
.
# T

(lbl)=
## A

## B

See §1 §2.
.
§1 -> A @lbl
§2 -> B
.

[C15-skipped-level]
.
# T

## A

#### Deep

### A2

See §1 §1.1 §1.2 §1.1.1.
.
§1 -> A
§1.1 -> Deep
§1.2 -> A2
§1.1.1 unresolved
.

[E2-title-and-subtitle]
.
# T

## A

### A1

See §1 §1.1.
.
§1 -> A
§1.1 -> A1
.

[E3-front-matter]
.
---
author: Me
---
# T

## A

### A1

See §1 §1.1.
.
§1 -> A
§1.1 -> A1
.

[E4-section-subtitles] docutils:sectsubtitle_xform=true
.
# T

## A

See §1.1 and §1.1.1.

### B

#### C

x
.
§1.1 -> B
§1.1.1 -> C
.

[E5-single-h2-root]
.
## A

### A1

See §1 §1.1.

#### A1a
.
§1 -> A1
§1.1 -> A1a
.

[E6-no-promotion]
.
See §1 §1.1.

# T

## A

### A1
.
§1 -> A
§1.1 -> A1
.

[E8-title-to-header] myst_title_to_header=true
.
---
title: Front
---
# H

## H1

See §1 §2 §2.1 §1.1.
.
§1 -> Front
§2 -> H
§2.1 -> H1
§1.1 unresolved
.

[P7-only-inactive] sphinx-only
.
# T

## A

```{only} latex
## Only1

### Only1a
```

## A3

See §1 §3.
.
§1 -> A
§3 -> A3
.

[P7-only-inactive-eval-rst] sphinx-only
.
# T

## A

```{eval-rst}
.. only:: latex

   Only1
   -----

   text
```

### A1b

## A2

See §1 §1.2 §2.
.
§1 -> A
§1.2 -> A1b
§2 -> A2
.

[P7-only-eval-rst-top-level] sphinx-only
.
See §1 §2.

```{eval-rst}
.. only:: html or not html

   A
   -

   B
   -
```
.
§1 -> A
§2 -> B
.

[P7-only-nested] sphinx-only
.
# T

## A

```{eval-rst}
.. only:: html or not html

   .. only:: html or not html

      Inner
      -----

      text
```

## B

See §1 §1.1 §2.
.
§1 -> A
§1.1 -> Inner
§2 -> B
.

[N1-ifconfig-eval-rst] sphinx-only sphinx:extensions=sphinx.ext.ifconfig
.
# T

## A

```{eval-rst}
.. ifconfig:: True

   IfSec
   -----

   text
```

## B

See §1 §1.1 §2.
.
§1 -> A
§1.1 -> IfSec
§2 -> B
.
