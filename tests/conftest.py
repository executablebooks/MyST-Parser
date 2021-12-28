"""Top-level configuration for pytest."""
try:
    import sphinx  # noqa: F401
except ImportError:
    pass
else:
    # only use when Sphinx is installed, to allow testing myst-docutils
    pytest_plugins = "sphinx.testing.fixtures"
