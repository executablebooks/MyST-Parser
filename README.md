# MyST-Parser

[![Github-CI][github-ci]][github-link]
[![Coverage][coveralls-badge]][coveralls-link]
[![Documentation Status][rtd-badge]][rtd-link]
[![Code style: black][black-badge]][black-link]
[![PyPI][pypi-badge]][pypi-link]
[![Conda][conda-badge]][conda-link]

An extended commonmark compliant parser, with bridges to docutils & sphinx.

## Usage

To install the MyST parser, run the following in a
[Conda environment](https://docs.conda.io) (recommended):

```bash
conda install -c conda-forge myst-parser
```

or

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

To use the MyST parser in Sphinx, simply add: `extensions = ["myst_parser"]` to your `conf.py`.

[github-ci]: https://github.com/ExecutableBookProject/MyST-Parser/workflows/Python%20package/badge.svg?branch=master
[github-link]: https://github.com/ExecutableBookProject/MyST-Parser
[coveralls-badge]: https://coveralls.io/repos/github/ExecutableBookProject/MyST-Parser/badge.svg?branch=master
[coveralls-link]: https://coveralls.io/github/ExecutableBookProject/MyST-Parser?branch=master
[rtd-badge]: https://readthedocs.org/projects/myst-parser/badge/?version=latest
[rtd-link]: https://myst-parser.readthedocs.io/en/latest/?badge=latest
[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[pypi-badge]: https://img.shields.io/pypi/v/myst-parser.svg
[pypi-link]: https://pypi.org/project/myst-parser
[conda-badge]: https://anaconda.org/conda-forge/myst-parser/badges/version.svg
[conda-link]: https://anaconda.org/conda-forge/myst-parser
[black-link]: https://github.com/ambv/black
