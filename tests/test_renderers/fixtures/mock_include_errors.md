Missing path:
.
```{include}
```
.
tmpdir/test.md:1: (ERROR/3) Directive 'include': 1 argument(s) required, 0 supplied
.

Non-existent path:
.
```{include} other.md
```
.
tmpdir/test.md:1: (SEVERE/4) Directive "include": file not found: 'tmpdir/other.md'
.

Error in include file:
.
```{include} bad.md
```
.
tmpdir/bad.md:1: (WARNING/2) Unknown interpreted text role "a". [myst.role_unknown]
.

Error line in include file:
.
```{include} bad_line3.md
```
.
tmpdir/bad_line3.md:3: (WARNING/2) Unknown interpreted text role "a". [myst.role_unknown]
.

Error line in include file, after content in the parent:
.
para

```{include} bad_line3.md
```
.
tmpdir/bad_line3.md:3: (WARNING/2) Unknown interpreted text role "a". [myst.role_unknown]
.

Error line in include file with start-line:
.
```{include} bad_skipped.md
:start-line: 2
```
.
tmpdir/bad_skipped.md:4: (WARNING/2) Unknown interpreted text role "a". [myst.role_unknown]
.

Error line in include file with front matter:
.
```{include} bad_frontmatter.md
```
.
tmpdir/bad_frontmatter.md:5: (WARNING/2) Unknown interpreted text role "a". [myst.role_unknown]
.

Error line in nested include file:
.
```{include} bad_outer.md
```
.
tmpdir/bad_inner.md:3: (WARNING/2) Unknown interpreted text role "a". [myst.role_unknown]
.

Error in include file with start-after:
.
```{include} bad_after.md
:start-after: START-HERE
```
.
tmpdir/bad_after.md:4: (WARNING/2) Unknown interpreted text role "a". [myst.role_unknown]
.

Error in include file with start-line and start-after:
.
```{include} bad_after.md
:start-line: 1
:start-after: START-HERE
```
.
tmpdir/bad_after.md:4: (WARNING/2) Unknown interpreted text role "a". [myst.role_unknown]
.

Error in include file with a multi-line start-after marker:
.
```{include} bad_marker2.md
---
start-after: "<!-- a -->\n<!-- b -->"
---
```
.
tmpdir/bad_marker2.md:5: (WARNING/2) Unknown interpreted text role "a". [myst.role_unknown]
.

Error in include file with a negative start-line:
.
```{include} bad_negative.md
:start-line: -2
```
.
tmpdir/bad_negative.md:5: (WARNING/2) Unknown interpreted text role "a". [myst.role_unknown]
.

Error in include file with a negative start-line beyond its length:
.
```{include} bad_negative.md
:start-line: -100
```
.
tmpdir/bad_negative.md:5: (WARNING/2) Unknown interpreted text role "a". [myst.role_unknown]
.

Error in CRLF include file with start-after:
.
```{include} bad_crlf.md
:start-after: MARK
```
.
tmpdir/bad_crlf.md:4: (WARNING/2) Unknown interpreted text role "a". [myst.role_unknown]
.

Error in include file with start-after and end-before:
.
```{include} bad_between.md
:start-after: START
:end-before: END
```
.
tmpdir/bad_between.md:5: (WARNING/2) Unknown interpreted text role "a". [myst.role_unknown]
.

No error when the start-after marker ends the file:
.
```{include} bad_between.md
:start-after: {c}`d`
```
.
.

Errors in a nested include file with start-line, and in the outer file after it:
.
```{include} bad_outer2.md
```
.
tmpdir/bad_inner2.md:4: (WARNING/2) Unknown interpreted text role "c". [myst.role_unknown]
tmpdir/bad_outer2.md:7: (WARNING/2) Unknown interpreted text role "a". [myst.role_unknown]
.
