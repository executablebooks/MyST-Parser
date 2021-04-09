"""myst-parser package setup."""
from importlib import import_module

from setuptools import find_packages, setup

setup(
    name="myst-parser",
    version=import_module("myst_parser").__version__,
    description=(
        "An extended commonmark compliant parser, " "with bridges to docutils & sphinx."
    ),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/executablebooks/MyST-Parser",
    project_urls={"Documentation": "https://myst-parser.readthedocs.io"},
    author="Chris Sewell",
    author_email="chrisj_sewell@hotmail.com",
    license="MIT",
    packages=find_packages(),
    entry_points={"console_scripts": ["myst-anchors = myst_parser.cli:print_anchors"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
        "Framework :: Sphinx :: Extension",
    ],
    keywords="markdown lexer parser development docutils sphinx",
    python_requires=">=3.6",
    install_requires=[
        "markdown-it-py~=0.6.2",
        "mdit-py-plugins~=0.2.5",
        "pyyaml",
        "jinja2",  # required for substitutions, but let sphinx choose version
        "docutils>=0.15",
        "sphinx>=2,<4",
    ],
    extras_require={
        "sphinx": [],  # left in for back-compatability
        "linkify": ["linkify-it-py~=1.0"],  # for use with "linkify" extension
        "code_style": ["flake8<3.8.0,>=3.7.0", "black", "pre-commit==1.17.0"],
        "testing": [
            "coverage",
            "pytest>=3.6,<4",
            "pytest-cov",
            "pytest-regressions",
            "beautifulsoup4",
            "docutils>=0.17",  # this version changes some HTML tags
        ],
        # Note: This is only required for internal use
        "rtd": [
            "sphinxcontrib-bibtex<2.0.0",
            "ipython",
            "sphinx-book-theme>=0.0.36",
            "sphinx-panels~=0.5.2",
        ],
    },
    zip_safe=True,
)
