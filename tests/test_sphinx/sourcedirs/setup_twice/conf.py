import os
import sys

sys.path.insert(0, os.path.abspath("."))

# ``myst_setup_again`` stands in for myst-nb,
# which calls myst_parser's ``setup_sphinx`` from its own setup
extensions = ["myst_parser", "myst_setup_again"]
exclude_patterns = ["_build"]
show_warning_types = True
