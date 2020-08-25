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

```{eval-rst}
.. _insidecodeblock:

I am inside the eval-rst fence

Referencing the :ref:`title`

Still inside the codeblock insidecodeblock_
```

I am outside the [fence](insidecodeblock)
