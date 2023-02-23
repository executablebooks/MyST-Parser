---
orphan: true
---

# Glossary

(units/length)=
## Length Units

The following length units are supported by the reStructuredText
parser:

* em (em unit, the element's font size)
* ex (ex unit, x-height of the element’s font)
* mm (millimeters; 1 mm = 1/1000 m)
* cm (centimeters; 1 cm = 10 mm)
* in (inches; 1 in = 2.54 cm = 96 px)
* px (pixels, 1 px = 1/96 in)
* pt (points; 1 pt = 1/72 in)
* pc (picas; 1 pc = 1/6 in = 12 pt)

This set corresponds to the length units in [CSS2] (a subset of length
units in [CSS3]).

The following are all valid length values: "1.5em", "20 mm", ".5in".

Length values without unit are completed with a writer-dependent
default (e.g. "px" with HTML, "pt" with `latex2e`).

[CSS2]: http://www.w3.org/TR/CSS2/syndata.html#length-units
[CSS3]: http://www.w3.org/TR/css-values-3/#absolute-lengths

(units/percentage)=
## Percentage Units

Percentage values have a percent sign ("%") as unit.  Percentage
values are relative to other values, depending on the context in which
they occur.
