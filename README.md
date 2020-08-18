# MyST-Parser

[![Github-CI][github-ci]][github-link]
[![Coverage Status][codecov-badge]][codecov-link]
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
pip install myst-parser
```

Or for package development:

```bash
git clone https://github.com/executablebooks/MyST-Parser
cd MyST-Parser
git checkout master
pip install -e .[code_style,testing,rtd]
```

To use the MyST parser in Sphinx, simply add: `extensions = ["myst_parser"]` to your `conf.py`.

## Contributing

We welcome all contributions!
See the [Contributing Guide](https://myst-parser.readthedocs.io/en/latest/master/contributing.html) for more details.

[github-ci]: https://github.com/executablebooks/MyST-Parser/workflows/continuous-integration/badge.svg?branch=master
[github-link]: https://github.com/executablebooks/MyST-Parser
[codecov-badge]: https://codecov.io/gh/executablebooks/MyST-Parser/branch/master/graph/badge.svg
[codecov-link]: https://codecov.io/gh/executablebooks/MyST-Parser
[rtd-badge]: https://readthedocs.org/projects/myst-parser/badge/?version=latest
[rtd-link]: https://myst-parser.readthedocs.io/en/latest/?badge=latest
[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[pypi-badge]: https://img.shields.io/pypi/v/myst-parser.svg
[pypi-link]: https://pypi.org/project/myst-parser
[conda-badge]: https://anaconda.org/conda-forge/myst-parser/badges/version.svg
[conda-link]: https://anaconda.org/conda-forge/myst-parser
[black-link]: https://github.com/ambv/black
