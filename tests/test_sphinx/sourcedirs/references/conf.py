extensions = ["myst_parser", "sphinx.ext.intersphinx"]
exclude_patterns = ["_build"]
myst_heading_anchors = 2

intersphinx_mapping = {
    "inter": ("https://example.com", "objects.inv"),
}

nitpick_ignore = [("myst", "unknown")]
