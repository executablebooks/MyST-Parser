# myst_parser

[![Build Status](https://travis-ci.org/ExecutableBookProject/myst_parser.svg?branch=master)](https://travis-ci.org/ExecutableBookProject/myst_parser)

An extended commonmark compliant parser, with bridges to docutils & sphinx.

## Installing

This parser currently requires the [ExecutableBookProject/mistletoe](https://github.com/ExecutableBookProject/mistletoe)
fork of mistletoe (and the myst branch).

```console
pip install git+https://github.com/ExecutableBookProject/mistletoe.git@myst
```

## Contributing

Code style is tested using [flake8](http://flake8.pycqa.org),
with the configuration set in `.flake8`,
and code formatted with [black](https://github.com/ambv/black).

Installing with `myst_parser[code_style]` makes the [pre-commit](https://pre-commit.com/)
package available, which will ensure this style is met before commits are submitted, by reformatting the code
and testing for lint errors.
It can be setup by:

```shell
>> cd myst_parser
>> pre-commit install
```

Optionally you can run `black` and `flake8` separately:

```shell
>> black .
>> flake8 .
```

Editors like VS Code also have automatic code reformat utilities, which can adhere to this standard.
