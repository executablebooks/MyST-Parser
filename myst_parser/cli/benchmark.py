import argparse
from importlib import import_module
from pathlib import Path
import re
from time import perf_counter

ALL_PACKAGES = (
    # "panflute",
    "python-markdown:extra",
    "commonmark.py",
    "mistletoe",
    "mistune",
    "markdown-it-py",
    "myst-parser:sphinx",
)
OPT_PACKAGES = ("myst-parser:html", "myst-parser:docutils")

DEFAULT_FILE = Path(__file__).parent.joinpath("spec.md")


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


@benchmark("panflute")
def run_panflute(package, text):
    return package.convert_text(text, input_format="markdown", output_format="html")


@benchmark("markdown_it")
def run_markdown_it_py(package, text):
    md = package.MarkdownIt("commonmark")
    return md.render(text)


@benchmark("myst_parser.main")
def run_myst_parser_html(package, text):
    package.to_html(text)


@benchmark("myst_parser.main")
def run_myst_parser_docutils(package, text):
    package.to_docutils(
        text, renderer="docutils", options={"ignore_missing_refs": True}
    )


@benchmark("myst_parser.main")
def run_myst_parser_sphinx(package, text):
    package.to_docutils(
        text,
        renderer="sphinx",
        options={"ignore_missing_refs": True},
        in_sphinx_env=True,
    )


def run_all(package_names, text, num_parses):
    prompt = "Running {} test(s) ...".format(len(package_names))
    print(prompt)
    print("=" * len(prompt))
    max_len = max(len(p) for p in package_names)
    for package_name in package_names:
        print(package_name + " " * (max_len - len(package_name)), end=" ")
        func_name = re.sub(r"[\.\-\:]", "_", package_name.lower())
        print(
            "{:.2f} s".format(globals()["run_{}".format(func_name)](text, num_parses))
        )
    return True


def main(args=None):
    parser = argparse.ArgumentParser(description="Run benchmark test.")
    parser.add_argument(
        "-f", "--file", default=None, type=str, help="the path to the file to parse"
    )
    parser.add_argument(
        "-n",
        "--num-parses",
        metavar="NPARSES",
        default=10,
        type=int,
        help="The number of parse iterations (default: 10)",
    )
    parser.add_argument(
        "-p",
        "--package",
        action="append",
        default=[],
        help="The package(s) to run (use -p multiple times).",
        choices=ALL_PACKAGES + OPT_PACKAGES,
        metavar="PACKAGE_NAME",
    )
    args = parser.parse_args(args)
    path = Path(args.file) if args.file else DEFAULT_FILE

    assert path.exists(), "path does not exist"
    print("Test document: {}".format(path.name))
    print("Test iterations: {}".format(args.num_parses))
    return run_all(args.package or ALL_PACKAGES, path.read_text(), args.num_parses)
