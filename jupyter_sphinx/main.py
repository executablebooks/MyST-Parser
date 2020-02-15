import pkg_resources
from typing import List, Optional, Set

from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.errors import ExtensionError

from jupyter_db import JupyterDB
from .components import (
    JupyterExec,
    JupyterExecNode,
    JupyterKernel,
    JupyterView,
    JupyterViewNode,
    ResolveJupyterViews,
)


def setup(app: Sphinx) -> dict:
    """Initialize Sphinx extension."""

    app.add_config_value("jupyter_sphinx_executor", "default", "html")

    # Document Elements
    app.add_directive("jupyter-kernel", JupyterKernel)
    app.add_directive("jupyter-exec", JupyterExec)
    app.add_directive("jupyter-view", JupyterView)
    app.add_node(
        JupyterExecNode,
        override=True,
        html=(lambda self, node: None, lambda self, node: None),
    )
    app.add_node(
        JupyterViewNode,
        override=True,
        html=(lambda self, node: None, lambda self, node: None),
    )

    # Read/Build Phases
    # -----------------
    # Emitted after the builder/environment has been created.
    app.connect("builder-inited", init_database)
    # Emitted when the files are determined that have been added, changed and removed
    app.connect("env-get-outdated", update_docs_in_db)
    # Emitted when the update() method of the build environment has completed,
    # that is, the environment and all doctrees are now up-to-date.
    app.connect("env-updated", execute_code_cells)
    # Applied per document, after the initial parsing of all documents
    # TODO check that post-transforms are applied to all documents
    add_transform(app, ResolveJupyterViews, True)

    return {
        "version": "0.1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
        "env_version": 1,
    }


def init_database(app: Sphinx):
    """Initialise a `JupyterDB`, if it does not exist yet"""
    if not hasattr(app.env, "jupyter_db"):
        # TODO add project options for cache initialisation
        app.env.jupyter_db = JupyterDB(app.doctreedir, echo=False)


def update_docs_in_db(
    app: Sphinx,
    env: BuildEnvironment,
    added: Set[str],
    changed: Set[str],
    removed: Set[str],
) -> List[str]:
    """Create new documents and remove changed/removed documents for database."""
    # TODO how to get extension of doc?
    for docname in added:
        app.env.jupyter_db.get_or_create_document(uri=docname)
    for docname in changed:
        # TODO could be more intelligent about rerunning docs; only if code has changed.
        app.env.jupyter_db.remove_document(uri=docname)
    for docname in removed:
        app.env.jupyter_db.remove_document(uri=docname)
    return []


def execute_code_cells(app: Sphinx, env: BuildEnvironment) -> Optional[List[str]]:
    name = app.config.jupyter_sphinx_executor
    entry_points = list(pkg_resources.iter_entry_points("jupyter_executors", name))
    if len(entry_points) == 0:
        raise ExtensionError(
            "'jupyter_executors.{}' entry point not found".format(name)
        )
    if len(entry_points) != 1:
        raise ExtensionError(
            "multiple 'jupyter_executors.{}' entry points found".format(name)
        )
    execute_func = entry_points[0].load()
    try:
        execute_func(app.env.jupyter_db)
    except Exception as err:
        raise ExtensionError(
            "'jupyter_executors.{}' failed: {}".format(name, err)
        ) from err


def add_transform(app, transform, post=False):
    transforms = app.registry.get_transforms()
    if transform not in transforms:
        if post:
            app.add_post_transform(transform)
        else:
            app.add_transform(transform)
