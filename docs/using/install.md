# Installing the MyST Parser

Installing the MyST parser provides access to two tools:

* A MyST-to-docutils parser and renderer.
* A Sphinx parser that utilizes the above tool in building your documenation.

To install the MyST parser, run the following:

```bash
pip install myst-parser[sphinx]
```

Or for package development:

```bash
git clone https://github.com/ExecutableBookProject/MyST-Parser
cd MyST-Parser
git checkout master
pip install -e .[sphinx,code_style,testing,rtd]
```
