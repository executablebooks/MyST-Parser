from docutils.nodes import make_id

extensions = ["myst_parser"]
exclude_patterns = ["_build"]
myst_heading_anchors = 2
myst_heading_slug_func = make_id
