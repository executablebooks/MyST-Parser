(develop/testing)=

# Testing Infrastructure

Where possible, additions to the code should be carried out in a
[test-driven development](https://en.wikipedia.org/wiki/Test-driven_development)
manner:

> **Write failing tests that the code should pass, then write code to pass the tests**.

The tests are run using [pytest](https://docs.pytest.org)/[GitHub Actions](https://github.com/features/actions) for unit tests, and [readthedocs](https://readthedocs.org/) for documentation build tests.

The tests are ordered in a hierarchical fashion:

1. In `tests/test_commonmark` the [CommonMark](https://github.com/commonmark/CommonMark.git) test set is run to check that the parser is complying with the CommonMark specification.
2. In `tests/test_renderers` are tests that check that the Markdown AST is being correctly converted to the docutils/sphinx AST. This includes testing that roles and directives are correctly parsed and run.
3. In `tests/test_sphinx` are tests that check that minimal sphinx project builds are running correctly, to convert MyST markdown files to HTML.
4. In `.circleci` the package documentation (written in MyST format) is built and tested for build errors/warnings.

## Test tools

[**pytest-regressions**](https://pytest-regressions.readthedocs.io) is a pytest plugin
that is used in the test suite, to maintain tests that generate lots of data.
In particular, they are used in the syntax testing to generate tests for AST trees
which may change in the future due to changes/additions to the data captured by the parser.
For example, after writing:

```python
def test_example_dict(data_regression):
    data_regression.check({
        "key1": "value1",
        "key2": "value2",
        "more": "data...",
    })
def test_example_str(file_regression):
    file_regression.check("a very long string...")
```

Running the following will initially fail,
but will also generate a file (per test) of expected output:

```console
$ pytest -k test_example
```

Subsequent times the tests are run, the tests output will now be validated against these stored files.

After a change to the syntax parser, all failing tests can then be 'regenerated' with the new
expected output, by running:

```console
$ pytest --force-regen
```
