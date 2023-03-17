(title)=

# Title with **nested** $a=1$

[](https://example.com)

[plain text](https://example.com)

[nested *syntax*](https://example.com)

[](title)

[plain text](title)

[nested *syntax*](title)

[](index.md)

[plain text](index.md)

[nested *syntax*](index.md)

[download **link**](file_link.txt)

[](subfolder/file_link2.txt)

```{eval-rst}
.. _insidecodeblock:

I am inside the eval-rst fence

Referencing the :ref:`title`

Still inside the codeblock insidecodeblock_
```

I am outside the [fence](insidecodeblock)

## Title *anchors*

```{toctree}
other.md
subfolder/other2.md
```

[](#title-anchors)

<project:#title-anchors>

[](./other.md#title-anchors)

[](other.md#title-anchors)

[](subfolder/other2.md#title-anchors)


# Intersphinx via `#`

Unknown [](#unknown)

Unknown explicit [**hallo**](#unknown)

Known no title [](#paragraph-target)

Known explicit [**hallo**](#paragraph-target)

Known with title [](#title-target)

Ambiguous [](#duplicate)

# Image in title ![badge](https://shields.io/or/something.svg)

[link up](#image-in-title-)
