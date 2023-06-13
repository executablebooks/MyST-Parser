# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import hashlib
from datetime import date
from pathlib import Path

from sphinx.application import Sphinx

from myst_parser import __version__

# -- Project information -----------------------------------------------------

project = "MyST Parser"
copyright = f"{date.today().year}, Executable Book Project"
author = "Executable Book Project"
version = __version__

master_doc = "index"
language = "en"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_parser",
    "autodoc2",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx_design",
    "sphinx_copybutton",
    "sphinxext.rediraffe",
    # disabled due to https://github.com/mgaitan/sphinxcontrib-mermaid/issues/109
    # "sphinxcontrib.mermaid",
    "sphinxext.opengraph",
    "sphinx_pyscript",
    "sphinx_tippy",
    "sphinx_togglebutton",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

suppress_warnings = ["myst.strikethrough"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3.7", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
    "markdown_it": ("https://markdown-it-py.readthedocs.io/en/latest", None),
}

# -- Autodoc settings ---------------------------------------------------

autodoc2_packages = [
    {
        "path": "../myst_parser",
        "exclude_files": ["_docs.py"],
    }
]
autodoc2_hidden_objects = ["dunder", "private", "inherited"]
autodoc2_replace_annotations = [
    ("re.Pattern", "typing.Pattern"),
    ("markdown_it.MarkdownIt", "markdown_it.main.MarkdownIt"),
]
autodoc2_replace_bases = [
    ("sphinx.directives.SphinxDirective", "sphinx.util.docutils.SphinxDirective"),
]
autodoc2_docstring_parser_regexes = [
    ("myst_parser", "myst"),
    (r"myst_parser\.setup", "myst"),
]
nitpicky = True
nitpick_ignore_regex = [
    (r"py:.*", r"docutils\..*"),
    (r"py:.*", r"pygments\..*"),
]
nitpick_ignore = [
    ("py:obj", "myst_parser._docs._ConfigBase"),
    ("py:exc", "MarkupError"),
    ("py:class", "sphinx.util.typing.Inventory"),
    ("py:class", "sphinx.writers.html.HTMLTranslator"),
    ("py:obj", "sphinx.transforms.post_transforms.ReferencesResolver"),
]

# -- MyST settings ---------------------------------------------------

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
    "attrs_inline",
    "attrs_block",
]
myst_url_schemes = {
    "http": None,
    "https": None,
    "mailto": None,
    "ftp": None,
    "wiki": "https://en.wikipedia.org/wiki/{{path}}#{{fragment}}",
    "doi": "https://doi.org/{{path}}",
    "gh-pr": {
        "url": "https://github.com/executablebooks/MyST-Parser/pull/{{path}}#{{fragment}}",
        "title": "PR #{{path}}",
        "classes": ["github"],
    },
    "gh-issue": {
        "url": "https://github.com/executablebooks/MyST-Parser/issue/{{path}}#{{fragment}}",
        "title": "Issue #{{path}}",
        "classes": ["github"],
    },
    "gh-user": {
        "url": "https://github.com/{{path}}",
        "title": "@{{path}}",
        "classes": ["github"],
    },
}
myst_number_code_blocks = ["typescript"]
myst_heading_anchors = 2
myst_footnote_transition = True
myst_dmath_double_inline = True
myst_enable_checkboxes = True
myst_substitutions = {
    "role": "[role](#syntax/roles)",
    "directive": "[directive](#syntax/directives)",
}

# -- HTML output -------------------------------------------------

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
    "use_issues_button": True,
    "announcement": "<b>v2.0.0</b> is now out! See the Changelog for details",
}
html_last_updated_fmt = ""
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
html_css_files = ["local.css"]

rediraffe_redirects = {
    "using/intro.md": "sphinx/intro.md",
    "syntax/syntax.md": "syntax/typography.md",
    "sphinx/intro.md": "intro.md",
    "using/use_api.md": "api/index.md",
    "api/index.md": "api/reference.rst",
    "api/reference.rst": "apidocs/index.md",
    "using/syntax.md": "syntax/syntax.md",
    "using/syntax-optional.md": "syntax/optional.md",
    "using/reference.md": "syntax/reference.md",
    "sphinx/reference.md": "configuration.md",
    "sphinx/index.md": "faq/index.md",
    "sphinx/use.md": "faq/index.md",
    "sphinx/faq.md": "faq/index.md",
    "explain/index.md": "develop/background.md",
}

tippy_skip_anchor_classes = ("headerlink", "sd-stretched-link", "sd-rounded-pill")
tippy_anchor_parent_selector = "article.bd-article"
tippy_rtd_urls = [
    "https://www.sphinx-doc.org/en/master",
    "https://markdown-it-py.readthedocs.io/en/latest",
]

# -- LaTeX output -------------------------------------------------

latex_engine = "xelatex"

# -- Local Sphinx extensions -------------------------------------------------


def setup(app: Sphinx):
    """Add functions to the Sphinx setup."""
    from myst_parser._docs import (
        DirectiveDoc,
        DocutilsCliHelpDirective,
        MystAdmonitionDirective,
        MystConfigDirective,
        MystExampleDirective,
        MystLexer,
        MystToHTMLDirective,
        MystWarningsDirective,
        NumberSections,
        StripUnsupportedLatex,
    )

    app.add_directive("myst-config", MystConfigDirective)
    app.add_directive("docutils-cli-help", DocutilsCliHelpDirective)
    app.add_directive("doc-directive", DirectiveDoc)
    app.add_directive("myst-warnings", MystWarningsDirective)
    app.add_directive("myst-example", MystExampleDirective)
    app.add_directive("myst-admonitions", MystAdmonitionDirective)
    app.add_directive("myst-to-html", MystToHTMLDirective)
    app.add_post_transform(StripUnsupportedLatex)
    app.add_post_transform(NumberSections)
    app.connect("html-page-context", add_version_to_css)
    app.add_lexer("myst", MystLexer)


def add_version_to_css(app: Sphinx, pagename, templatename, context, doctree):
    """Add the version number to the local.css file, to bust the cache for changes."""
    if app.builder.name != "html":
        return
    if "_static/local.css" in context.get("css_files", {}):
        css = Path(app.srcdir, "_static/local.css").read_text("utf8")
        hashed = hashlib.sha256(css.encode("utf-8")).hexdigest()
        index = context["css_files"].index("_static/local.css")
        context["css_files"][index] = f"_static/local.css?hash={hashed}"
