# Installing the MyST Parser

Installing the MyST parser provides access to two tools:

* A MyST-to-docutils parser and renderer.
* A Sphinx parser that utilizes the above tool in building your documenation.

To install the MyST parser, run the following:

```bash
pip install -e "git+https://github.com/ExecutableBookProject/myst_parser.git#egg=myst_parser[sphinx]"
```

Or for package development:

```bash
git clone https://github.com/ExecutableBookProject/myst_parser
cd myst_parser
git checkout develop
pip install -e .[sphinx,code_style,testing,rtd]
```

This should install the myst fork of mistletoe, along with the Sphinx parser
that is included in the "extensions" configuration of this site.
