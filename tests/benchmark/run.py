#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from importlib import import_module
import sys
from time import perf_counter


DEFAULT_TEST_FILE = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        os.pardir,
        "docs",
        "examples",
        "benchmark.md",
    )
)
TIMES = 1000


def benchmark(package_name, version=None):
    def decorator(func):
        def inner():
            try:
                package = import_module(package_name.split(":")[0])
                print("(" + (version or package.__version__) + ")", end=": ")
            except ImportError:
                return "not available."
            start = perf_counter()
            for i in range(TIMES):
                func(package)
            end = perf_counter()

            return end - start

        return inner

    return decorator


@benchmark("markdown")
def run_markdown_py(package):
    with open(DEFAULT_TEST_FILE, "r") as fin:
        return package.markdown(fin.read())  # ["extra"])


@benchmark("mistune")
def run_mistune(package):
    with open(DEFAULT_TEST_FILE, "r") as fin:
        return package.markdown(fin.read())


@benchmark("commonmark", "0.9.1")
def run_commonmark(package):
    with open(DEFAULT_TEST_FILE, "r") as fin:
        return package.commonmark(fin.read())


@benchmark("mistletoe")
def run_mistletoe(package):
    with open(DEFAULT_TEST_FILE, "r") as fin:
        return package.markdown(fin)


@benchmark("myst_parser:html")
def run_myst_parser_html(package):
    with open(DEFAULT_TEST_FILE, "r") as fin:
        package.parse_text(fin, "html")


@benchmark("myst_parser:docutils")
def run_myst_parser_docutils(package):
    with open(DEFAULT_TEST_FILE, "r") as fin:
        package.parse_text(fin, "docutils", config={"ignore_missing_refs": True})


@benchmark("myst_parser:sphinx")
def run_myst_parser_sphinx(package):
    with open(DEFAULT_TEST_FILE, "r") as fin:
        package.parse_text(fin, "sphinx", load_sphinx_env=True)


def run(package_name):
    print(package_name, end=" ")
    print("{:.2f} s".format(globals()["run_{}".format(package_name.lower())]()))


def run_all(package_names):
    prompt = "Running tests ..."  # .format(", ".join(package_names))
    print(prompt)
    print("=" * len(prompt))
    for package_name in package_names:
        run(package_name)


def main(*args):
    print("Test document: {}".format(os.path.basename(DEFAULT_TEST_FILE)))
    print("Test iterations: {}".format(TIMES))
    if args[1:]:
        run_all(args[1:])
    else:
        run_all(
            [
                "markdown_py",
                "mistune",
                "commonmark",
                "mistletoe",
                "myst_parser_html",
                "myst_parser_docutils",
                "myst_parser_sphinx",
            ]
        )


if __name__ == "__main__":
    main(*sys.argv)
