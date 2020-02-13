# myst_parser

[![Build Status](https://travis-ci.org/ExecutableBookProject/myst_parser.svg?branch=master)](https://travis-ci.org/ExecutableBookProject/myst_parser)
[![Coverage Status](https://coveralls.io/repos/github/ExecutableBookProject/myst_parser/badge.svg?branch=improvements)](https://coveralls.io/github/ExecutableBookProject/myst_parser?branch=improvements)
[![Documentation Status](https://readthedocs.org/projects/myst-parser/badge/?version=latest)](https://myst-parser.readthedocs.io/en/latest/?badge=latest)

An extended commonmark compliant parser, with bridges to docutils & sphinx.

## Usage

```console
pip install -e git+https://github.com/ExecutableBookProject/myst_parser.git#egg=myst_parser[sphinx,code_style,testing]
```

Note, this parser currently requires the [ExecutableBookProject/mistletoe](https://github.com/ExecutableBookProject/mistletoe)
fork of mistletoe (included in the above installation).

To use the Myst parser in sphinx, simply add: `extensions = ["myst_parser"]` to your `conf.py`.

## Parsed Token Classes

For more information, also see the [CommonMark Spec](https://spec.commonmark.org/0.28/).

### Block Tokens

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

### Pull Requests

To contribute, make Pull Requests to the `develop` branch (this is the default branch). A PR can consist of one or multiple commits. Before you open a PR, make sure to clean up your commit history and create the commits that you think best divide up the total work as outlined above (use `git rebase` and `git commit --amend`). Ensure all commit messages clearly summarise the changes in the header and the problem that this commit is solving in the body.

Merging pull requests: There are three ways of 'merging' pull requests on GitHub:

- Squash and merge: take all commits, squash them into a single one and put it on top of the base branch.
    Choose this for pull requests that address a single issue and are well represented by a single commit.
    Make sure to clean the commit message (title & body)
- Rebase and merge: take all commits and 'recreate' them on top of the base branch. All commits will be recreated with new hashes.
    Choose this for pull requests that require more than a single commit.
    Examples: PRs that contain multiple commits with individually significant changes; PRs that have commits from different authors (squashing commits would remove attribution)
- Merge with merge commit: put all commits as they are on the base branch, with a merge commit on top
    Choose for collaborative PRs with many commits. Here, the merge commit provides actual benefits.
