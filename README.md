# MyST-Parser

[![CI Status][travis-badge]][travis-link]
[![Coverage][coveralls-badge]][coveralls-link]
[![Documentation Status][rtd-badge]][rtd-link]
[![Code style: black][black-badge]][black-link]
[![PyPI][pypi-badge]][pypi-link]
<!-- [![Conda][conda-badge]][conda-link] -->

An extended commonmark compliant parser, with bridges to docutils & sphinx.

## Usage

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

## Parsed Token Classes

For more information, also see the [CommonMark Spec](https://spec.commonmark.org/0.28/).

### Block Tokens

- **FrontMatter**: A YAML block at the start of the document enclosed by `---`
- **HTMLBlock**: Any valid HTML (rendered in HTML output only)
- **LineComment**: `% this is a comment`
- **BlockCode**: indented text (4 spaces)
- **Heading**: `# Heading` (levels 1-6)
- **SetextHeading**: underlined header
- **Quote**: `> this is a quote`
- **CodeFence**: enclosed in 3 or more backticks.
  If it starts with a `{name}`, then treated as directive.
- **ThematicBreak**: `---`
- **List**: bullet points or enumerated.
- **Table**: Standard markdown table styles.
- **Footnote**: A substitution for an inline link (e.g. `[key][name]`), which can have a reference target (no spaces), and an optional title (in `"`), e.g. `[key]: https://www.google.com "a title"`
- **Paragraph**: General inline text

### Span (Inline) Tokens

- **Role**: `` `{name}`interpreted text` ``
- **Math**: `$a=1$` or `$$a=1$$`
- **HTMLSpan**: any valid HTML (rendered in HTML output only)
- **EscapeSequence**: `\*`
- **AutoLink**: `<http://www.google.com>`
- **Target**: `(target)=` (precedes element to target, e.g. header)
- **InlineCode**: `` `a=1` ``
- **LineBreak**: Soft or hard (ends with spaces or `\`)
- **Image**: `![alt](src "title")`
- **Link**: `[text](target "title")` or `[text][key]` (key from `Footnote`)
- **Strong**: `**strong**`
- **Emphasis**: `*emphasis*`
- **RawText**

## Contributing

### Code Style

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

### Pull Requests

To contribute, make Pull Requests to the `master` branch (this is the default branch). A PR can consist of one or multiple commits. Before you open a PR, make sure to clean up your commit history and create the commits that you think best divide up the total work as outlined above (use `git rebase` and `git commit --amend`). Ensure all commit messages clearly summarise the changes in the header and the problem that this commit is solving in the body.

Merging pull requests: There are three ways of 'merging' pull requests on GitHub:

- Squash and merge: take all commits, squash them into a single one and put it on top of the base branch.
    Choose this for pull requests that address a single issue and are well represented by a single commit.
    Make sure to clean the commit message (title & body)
- Rebase and merge: take all commits and 'recreate' them on top of the base branch. All commits will be recreated with new hashes.
    Choose this for pull requests that require more than a single commit.
    Examples: PRs that contain multiple commits with individually significant changes; PRs that have commits from different authors (squashing commits would remove attribution)
- Merge with merge commit: put all commits as they are on the base branch, with a merge commit on top
    Choose for collaborative PRs with many commits. Here, the merge commit provides actual benefits.


[travis-badge]: https://travis-ci.org/ExecutableBookProject/MyST-Parser.svg?branch=master
[travis-link]: https://travis-ci.org/ExecutableBookProject/MyST-Parser
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
