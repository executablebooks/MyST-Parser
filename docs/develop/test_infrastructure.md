# Testing Infrastructure

Where possible, additions to the code should be carried out in a
[test-driven development](https://en.wikipedia.org/wiki/Test-driven_development)
manner:

> **Write failing tests that the code should pass, then write code to pass the tests**.

The tests are run using [pytest](https://docs.pytest.org)/[TravisCI](https://travis-ci.org) for unit tests, and [sphinx-build](https://www.sphinx-doc.org/en/master/man/sphinx-build.html)/[CircleCI](https://circleci.com) for documentation build tests.

The tests are ordered in a hierarchical fashion:

1. In `tests/test_syntax` are tests that check that the source text is being correctly converted to the Markdown ([mistletoe](https://github.com/miyuchina/mistletoe)) AST.
2. In `tests/test_commonmark` the [CommonMark](https://github.com/commonmark/CommonMark.git) test set is run; to check that the parser is complying with the CommonMark specification.
3. In `tests/test_renderers` are tests that check that the Markdown AST is being correctly converted to the docutils/sphinx AST. This includes testing that roles and directives are correctly parsed and run.
4. In `tests/test_sphinx` are tests that check that minimal sphinx project builds are running correctly, to convert myst markdown files to HTML.
5. In `.circleci` the package documentation (written in myst format) is built and tested for build errors/warnings.
