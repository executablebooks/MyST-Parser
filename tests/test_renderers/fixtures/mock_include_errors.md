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
