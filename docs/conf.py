# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = "MyST Parser"
copyright = "2020, Executable Book Project"
author = "Executable Book Project"

master_doc = "index"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinxcontrib.bibtex",
    "sphinx_tabs.tabs",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_book_theme"
html_logo = "_static/logo.png"
html_theme_options = {
    "github_url": "https://github.com/executablebooks/MyST-Parser",
    "repository_url": "https://github.com/executablebooks/MyST-Parser",
    "expand_sections": ["examples/index"],
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


def run_apidoc(app):
    """ generate apidoc

    See: https://github.com/rtfd/readthedocs.org/issues/1139
    """
    import os
    import shutil
    import sphinx
    from sphinx.ext import apidoc

    logger = sphinx.util.logging.getLogger(__name__)
    logger.info("running apidoc")
    # get correct paths
    this_folder = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    api_folder = os.path.join(this_folder, "_api")
    module_path = os.path.normpath(os.path.join(this_folder, "../"))
    ignore_paths = ["../setup.py", "../conftest.py", "../tests"]
    ignore_paths = [
        os.path.normpath(os.path.join(this_folder, p)) for p in ignore_paths
    ]

    if os.path.exists(api_folder):
        shutil.rmtree(api_folder)
    os.mkdir(api_folder)

    argv = ["-M", "--separate", "-o", api_folder, module_path] + ignore_paths

    apidoc.main(argv)

    # we don't use this
    if os.path.exists(os.path.join(api_folder, "modules.rst")):
        os.remove(os.path.join(api_folder, "modules.rst"))


intersphinx_mapping = {
    "python": ("https://docs.python.org/3.7", None),
    "mistletoe": ("https://mistletoe-ebp.readthedocs.io/en/latest", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
}

# autodoc_default_options = {
#     "show-inheritance": True,
#     "special-members": "__init__, __enter__, __exit__",
#     "members": True,
#     # 'exclude-members': '',
#     "undoc-members": True,
#     # 'inherited-members': True
# }
autodoc_member_order = "bysource"

nitpick_ignore = [
    ("py:class", "Any"),
    ("py:class", "Tuple"),
    ("py:class", "ForwardRef"),
    ("py:class", "NoneType"),
    ("py:class", "TableRow"),
]


def setup(app):
    """Add functions to the Sphinx setup."""
    # app.connect("builder-inited", run_apidoc)
