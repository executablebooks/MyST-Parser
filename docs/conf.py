# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from datetime import date
from functools import partial
from pathlib import Path

from setuptools_scm import get_version
from sphinx.application import Sphinx

# -- Path setup --------------------------------------------------------------

PROJECT_ROOT_DIR = Path(__file__).parents[1].resolve()  # pylint: disable=no-member
get_scm_version = partial(get_version, root=PROJECT_ROOT_DIR)
# -- Project information -----------------------------------------------------

github_url = "https://github.com"
github_repo_org = "ansible"
github_repo_name = "ansible-language-server"
github_repo_slug = f"{github_repo_org}/{github_repo_name}"
github_repo_url = f"{github_url}/{github_repo_slug}"
github_sponsors_url = f"{github_url}/sponsors"

project = "MyST Parser"
copyright = f"{date.today().year}, Executable Book Project"
author = "Executable Book Project"

# The short X.Y version
version = ".".join(
    get_scm_version(local_scheme="no-local-version",).split(
        "."
    )[:3],
)

# The full version, including alpha/beta/rc tags
release = get_scm_version()


master_doc = "index"
language = "en"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_design",
    "sphinxext.rediraffe",
    "sphinxcontrib.mermaid",
    "sphinxext.opengraph",
    "sphinxcontrib.towncrier",  # provides `towncrier-draft-entries` directive
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "changelog-fragments.d/**",  # Towncrier-managed change notes
]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_book_theme"
html_logo = "_static/logo-wide.svg"
html_favicon = "_static/logo-square.svg"
html_title = ""
html_theme_options = {
    "home_page_in_toc": True,
    "github_url": "https://github.com/executablebooks/MyST-Parser",
    "repository_url": "https://github.com/executablebooks/MyST-Parser",
    "repository_branch": "master",
    "path_to_docs": "docs",
    "use_repository_button": True,
    "use_edit_page_button": True,
}
# OpenGraph metadata
ogp_site_url = "https://myst-parser.readthedocs.io/en/latest"
# This is the image that GitHub stores for our social media previews
ogp_image = "https://repository-images.githubusercontent.com/240151150/316bc480-cc23-11eb-96fc-4ab2f981a65d"  # noqa: E501
ogp_custom_meta_tags = [
    '<meta name="twitter:card" content="summary_large_image">',
]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

myst_enable_extensions = [
    "dollarmath",
    "amsmath",
    "deflist",
    "fieldlist",
    "html_admonition",
    "html_image",
    "colon_fence",
    "smartquotes",
    "replacements",
    "linkify",
    "strikethrough",
    "substitution",
    "tasklist",
    "attrs_image",
]
myst_number_code_blocks = ["typescript"]
myst_substitutions = {
    "project": project,
    "release": release,
    "release_l": f"`{release}`",  # Needed in draft changelog for spelling ext
    "version": version,
}
myst_heading_anchors = 2
myst_footnote_transition = True
myst_dmath_double_inline = True

rediraffe_redirects = {
    "using/intro.md": "sphinx/intro.md",
    "sphinx/intro.md": "intro.md",
    "using/use_api.md": "api/index.md",
    "api/index.md": "api/reference.rst",
    "using/syntax.md": "syntax/syntax.md",
    "using/syntax-optional.md": "syntax/optional.md",
    "using/reference.md": "syntax/reference.md",
    "sphinx/reference.md": "configuration.md",
    "sphinx/index.md": "faq/index.md",
    "sphinx/use.md": "faq/index.md",
    "sphinx/faq.md": "faq/index.md",
    "explain/index.md": "develop/background.md",
}

suppress_warnings = ["myst.strikethrough"]

# -- Options for towncrier_draft extension -----------------------------------

towncrier_draft_autoversion_mode = "draft"  # or: 'sphinx-version', 'sphinx-release'
towncrier_draft_include_empty = True
towncrier_draft_working_directory = PROJECT_ROOT_DIR
# towncrier_draft_config_path = 'pyproject.toml'  # relative to cwd

# -- Options for extlinks extension ------------------------------------------

extlinks = {
    "issue": (f"{github_repo_url}/issues/%s", "#%s"),  # noqa: WPS323
    "pr": (f"{github_repo_url}/pull/%s", "PR #%s"),  # noqa: WPS323
    "commit": (f"{github_repo_url}/commit/%s", "%s"),  # noqa: WPS323
    "gh": (f"{github_url}/%s", "GitHub: %s"),  # noqa: WPS323
    "user": (f"{github_sponsors_url}/%s", "@%s"),  # noqa: WPS323
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3.7", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
    "markdown_it": ("https://markdown-it-py.readthedocs.io/en/latest", None),
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
nitpicky = True
nitpick_ignore = [
    ("py:class", "docutils.nodes.document"),
    ("py:class", "docutils.nodes.docinfo"),
    ("py:class", "docutils.nodes.Element"),
    ("py:class", "docutils.nodes.Node"),
    ("py:class", "docutils.nodes.field_list"),
    ("py:class", "docutils.nodes.problematic"),
    ("py:class", "docutils.nodes.pending"),
    ("py:class", "docutils.nodes.system_message"),
    ("py:class", "docutils.statemachine.StringList"),
    ("py:class", "docutils.parsers.rst.directives.misc.Include"),
    ("py:class", "docutils.parsers.rst.Parser"),
    ("py:class", "docutils.utils.Reporter"),
    ("py:class", "nodes.Element"),
    ("py:class", "nodes.Node"),
    ("py:class", "nodes.system_message"),
    ("py:class", "Directive"),
    ("py:class", "Include"),
    ("py:class", "StringList"),
    ("py:class", "DocutilsRenderer"),
    ("py:class", "MockStateMachine"),
]


def setup(app: Sphinx):
    """Add functions to the Sphinx setup."""
    from myst_parser._docs import (
        DirectiveDoc,
        DocutilsCliHelpDirective,
        MystConfigDirective,
    )

    app.add_css_file("custom.css")
    app.add_directive("myst-config", MystConfigDirective)
    app.add_directive("docutils-cli-help", DocutilsCliHelpDirective)
    app.add_directive("doc-directive", DirectiveDoc)
