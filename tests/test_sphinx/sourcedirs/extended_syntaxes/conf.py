extensions = ["myst_parser"]
language = "en"
exclude_patterns = ["_build"]
myst_disable_syntax = ["emphasis"]
myst_dmath_allow_space = False
myst_dmath_double_inline = True
mathjax_config = {}
myst_enable_extensions = [
    "dollarmath",
    "amsmath",
    "deflist",
    "colon_fence",
    "linkify",
    "tasklist",
]
myst_html_meta = {
    "description lang=en": "meta description",
    "property=og:locale": "en_US",
}
