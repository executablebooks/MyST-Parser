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
tmpdir/bad.md:2: (WARNING/2) Unknown interpreted text role "a". [myst.role_unknown]
.
