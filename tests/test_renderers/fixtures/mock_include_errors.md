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

Error in include file with start line:
.
```{include} bad_start.md
:start-line: 1
```
.
tmpdir/bad_start.md:2: (WARNING/2) Unknown interpreted text role "a". [myst.role_unknown]
.

Error in nested include file:
.
```{include} outer.md
```
.
tmpdir/bad.md:1: (WARNING/2) Unknown interpreted text role "a". [myst.role_unknown]
.
