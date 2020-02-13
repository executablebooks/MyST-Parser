Welcome to myst's documentation!
================================

A little site to test out the Myst Sphinx parser. This will probably uncover
some bugs, so please report them [here](https://github.com/ExecutableBookProject/meta/issues/24)
if you find any more.

## Installing the Myst parser

To install the myst parser (and thus to be able to build these docs),
run the following:

```bash
git clone https://github.com/chrisjsewell/mistletoe
cd mistletoe
git checkout myst
pip install .[sphinx,testing]
```

This should install the myst fork of mistletoe, along with the Sphinx parser
that is included in the "extensions" configuration of this site.

Here are the site contents:

```{toctree}
---
maxdepth: 2
caption: Contents
---
wealth_dynamics_rst.rst
wealth_dynamics_md.md
examples.md
```
