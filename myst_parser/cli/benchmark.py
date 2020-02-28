import argparse
from importlib import import_module
import os
import re
from time import perf_counter

ALL_PACKAGES = (
    "python-markdown:extra",
    "mistune",
    "commonmark.py",
    "mistletoe",
    "myst_parser:html",
    "myst_parser:docutils",
    "myst_parser:sphinx",
)


def benchmark(package_name, version=None):
    def decorator(func):
        def inner(text, num_parses):
            try:
                package = import_module(package_name)
                print("(" + (version or package.__version__) + ")", end=": ")
            except ImportError:
                return "not available."
            start = perf_counter()
            for i in range(num_parses):
                func(package, text)
            end = perf_counter()

            return end - start

        return inner

    return decorator


@benchmark("markdown")
def run_python_markdown_extra(package, text):
    return package.markdown(text, extensions=["extra"])


@benchmark("mistune")
def run_mistune(package, text):
    return package.markdown(text)


@benchmark("commonmark", "0.9.1")
def run_commonmark_py(package, text):
    return package.commonmark(text)


@benchmark("mistletoe")
def run_mistletoe(package, text):
    return package.markdown(text)


@benchmark("myst_parser")
def run_myst_parser_html(package, text):
    package.parse_text(text, "html")


@benchmark("myst_parser")
def run_myst_parser_docutils(package, text):
    package.parse_text(text, "docutils", config={"ignore_missing_refs": True})


@benchmark("myst_parser")
def run_myst_parser_sphinx(package, text):
    package.parse_text(text, "sphinx", load_sphinx_env=True)


def run_all(package_names, text, num_parses):
    prompt = "Running {} test(s) ...".format(len(package_names))
    print(prompt)
    print("=" * len(prompt))
    for package_name in package_names:
        print(package_name, end=" ")
        func_name = re.sub(r"[\.\-\:]", "_", package_name.lower())
        print(
            "{:.2f} s".format(globals()["run_{}".format(func_name)](text, num_parses))
        )
    return True


def main(args=None):
    parser = argparse.ArgumentParser(description="Run benchmark test.")
    parser.add_argument("path", type=str, help="the path to the file to parse")
    parser.add_argument(
        "-n",
        "--num-parses",
        metavar="NPARSES",
        default=1000,
        type=int,
        help="The number of parse iterations (default: 1000)",
    )
    parser.add_argument(
        "-p",
        "--package",
        action="append",
        default=[],
        help="The package(s) to run (use -p multiple times).",
        choices=ALL_PACKAGES,
        metavar="PACKAGE_NAME",
    )
    args = parser.parse_args(args)

    assert os.path.exists(args.path), "path does not exist"
    print("Test document: {}".format(os.path.basename(args.path)))
    print("Test iterations: {}".format(args.num_parses))
    with open(args.path, "r") as handle:
        text = handle.read()
    return run_all(args.package or ALL_PACKAGES, text, args.num_parses)
