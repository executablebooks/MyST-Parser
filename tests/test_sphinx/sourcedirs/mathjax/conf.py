import sphinx

extensions = ["myst_parser"]
exclude_patterns = ["_build"]

if sphinx.version_info[0] <= 3:
    mathjax_config = {"tex2jax": {"processClass": "other"}}
else:
    mathjax3_config = {"options": {"processHtmlClass": "other"}}

# this should remove the warning
# suppress_warnings = ["myst.mathjax"]
