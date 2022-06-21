# Contributing

[![Github-CI][github-ci]][github-link]
[![Coverage Status][codecov-badge]][codecov-link]
[![Documentation Status][rtd-badge]][rtd-link]
[![Code style: black][black-badge]][black-link]

We welcome all contributions!
See the [EBP Contributing Guide](https://executablebooks.org/en/latest/contributing.html) for general details, and below for guidance specific to MyST-Parser.

## Install for development

To install `myst-parser` for development, take the following steps:

```bash
git clone https://github.com/executablebooks/MyST-Parser
cd MyST-Parser
git checkout master
pip install -e .[code_style,testing,rtd]
```

## Code Style

Code style is tested using [flake8](http://flake8.pycqa.org),
with the configuration set in `.flake8`,
and code formatted with [black](https://github.com/ambv/black).

Installing with `myst-parser[code_style]` makes the [pre-commit](https://pre-commit.com/)
package available, which will ensure this style is met before commits are submitted, by reformatting the code
and testing for lint errors.
It can be setup by:

```shell
>> cd MyST-Parser
>> pre-commit install
```

Optionally you can run `black` and `flake8` separately:

```shell
>> black .
>> flake8 .
```

Editors like VS Code also have automatic code reformat utilities, which can adhere to this standard.

All functions and class methods should be annotated with types and include a docstring. The preferred docstring format is outlined in `MyST-Parser/docstring.fmt.mustache` and can be used automatically with the
[autodocstring](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring) VS Code extension.

## Testing

For code tests, myst-parser uses [pytest](https://docs.pytest.org):

```shell
>> cd MyST-Parser
>> pytest
```

You can also use [tox](https://tox.readthedocs.io), to run the tests in multiple isolated environments (see the `tox.ini` file for available test environments):

```shell
>> cd MyST-Parser
>> tox
```

For documentation build tests:

```shell
>> cd MyST-Parser/docs
>> make clean
>> make html-strict
```

```{seealso}
{ref}`develop/testing`
```

[github-ci]: https://github.com/executablebooks/MyST-Parser/workflows/continuous-integration/badge.svg?branch=master
[github-link]: https://github.com/executablebooks/MyST-Parser
[codecov-badge]: https://codecov.io/gh/executablebooks/MyST-Parser/branch/master/graph/badge.svg
[codecov-link]: https://codecov.io/gh/executablebooks/MyST-Parser
[rtd-badge]: https://readthedocs.org/projects/myst-parser/badge/?version=latest
[rtd-link]: https://myst-parser.readthedocs.io/en/latest/?badge=latest
[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[black-link]: https://github.com/ambv/black
