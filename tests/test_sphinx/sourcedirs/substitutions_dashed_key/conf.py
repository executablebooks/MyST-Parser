extensions = ["myst_parser"]
exclude_patterns = ["_build"]
myst_enable_extensions = ["substitution"]
myst_substitutions = {
    "foo-bar": "Foobar",
    "plain": "PlainValue",
    "circ-a": "{{circ-b}}",
    "circ-b": "{{circ-a}}",
}
