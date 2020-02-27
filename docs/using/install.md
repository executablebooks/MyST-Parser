# Installing the MyST Parser

Installing the MyST parser provides access to two tools:

* A MyST-to-docutils parser and renderer.
* A Sphinx parser that utilizes the above tool in building your documenation.

To install the MyST parser, run the following:

```bash
pip install -e "git+https://github.com/ExecutableBookProject/MyST-Parser.git#egg=myst-parser[sphinx]"
```

Or for package development:

```bash
git clone https://github.com/ExecutableBookProject/MyST-Parser
cd MyST-Parser
git checkout develop
pip install -e .[sphinx,code_style,testing,rtd]
```

This should install the myst fork of mistletoe, along with the Sphinx parser
that is included in the "extensions" configuration of this site.

## Using Myst Parser with Sphinx

Sphinx is a documentation generator for building a website or book from multiple source documents and assets. To get started with Sphinx, see their [Quickstart Guide](https://www.sphinx-doc.org/en/master/usage/quickstart.html).

To use the MyST parser in Sphinx, simply add: `extensions = ["myst_parser"]` to your `conf.py`.
