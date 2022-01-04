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
tmpdir/test.md:1: (SEVERE/4) Directive "include": error reading file: tmpdir/other.md
[Errno 2] No such file or directory: 'tmpdir/other.md'.
.

Error in include file:
.
```{include} bad.md
```
.
tmpdir/bad.md:2: (ERROR/3) Unknown interpreted text role "a".
.
