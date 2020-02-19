from unittest import mock

import pytest

from myst_parser.docutils_renderer import SphinxRenderer


@pytest.fixture
def renderer():
    renderer = SphinxRenderer()
    with renderer:
        yield renderer


@pytest.fixture
def renderer_mock():
    renderer = SphinxRenderer()
    renderer.render_inner = mock.Mock(return_value="inner")
    with renderer:
        yield renderer


@pytest.fixture
def sphinx_renderer(renderer):
    from sphinx.util.docutils import docutils_namespace, sphinx_domains

    with docutils_namespace():
        app = renderer.mock_sphinx_env()
        with sphinx_domains(app.env):
            yield renderer
