"""myst_parser package setup."""
from importlib import import_module

from setuptools import find_packages, setup

setup(
    name="myst_parser",
    version=import_module("myst_parser").__version__,
    description=(
        "An extended commonmark compliant parser, " "with bridges to docutils & sphinx."
    ),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ExecutableBookProject/myst_parser",
    author="Chris Sewell",
    author_email="chrisj_sewell@hotmail.com",
    license="MIT",
    packages=find_packages(),
    entry_points={"console_scripts": []},
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
    ],
    keywords="markdown lexer parser development docutils sphinx",
    python_requires=">=3.5",
    install_requires=[
        (
            "mistletoe @ "
            "https://github.com/ExecutableBookProject/mistletoe/archive/myst.zip"
        )
    ],
    extras_require={
        "code_style": ["flake8<3.8.0,>=3.7.0", "black", "pre-commit==1.17.0"],
        "testing": [
            "coverage",
            "pytest>=3.6,<4",
            "pytest-cov",
            "pytest-regressions",
            "beautifulsoup4",
        ],
        "sphinx": ["pyyaml", "docutils>=0.15", "sphinx>=2,<3", "sphinxcontrib-bibtex"],
    },
    zip_safe=True,
)
