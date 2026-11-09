"""A local extension that runs myst-parser's Sphinx setup a second time.

This is what myst-nb does, so listing both ``myst_parser`` and ``myst_nb``
in ``extensions`` calls ``setup_sphinx`` twice on the same application.
"""

from myst_parser.sphinx_ext.main import setup_sphinx


def setup(app):
    setup_sphinx(app)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
