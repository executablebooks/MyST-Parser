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
    url="https://github.com/ExecutableBookProject/MyST-Parser",
    project_urls={"Documentation": "https://myst-parser.readthedocs.io"},
    author="Chris Sewell",
    author_email="chrisj_sewell@hotmail.com",
    license="MIT",
    packages=find_packages(),
    entry_points={
        "console_scripts": ["myst-benchmark = myst_parser.cli.benchmark:main"]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
        "Framework :: Sphinx :: Extension",
    ],
    keywords="markdown lexer parser development docutils sphinx",
    python_requires=">=3.6",
    install_requires=["markdown-it-py~=0.4.5"],
    extras_require={
        "sphinx": ["pyyaml", "docutils>=0.15", "sphinx>=2,<3"],
        "code_style": ["flake8<3.8.0,>=3.7.0", "black", "pre-commit==1.17.0"],
        "testing": [
            "coverage",
            "pytest>=3.6,<4",
            "pytest-cov",
            "pytest-regressions",
            "beautifulsoup4",
        ],
        "rtd": ["sphinxcontrib-bibtex", "ipython", "pydata-sphinx-theme"],
    },
    zip_safe=True,
)
