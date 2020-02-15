import json

from jupyter_db import main as jdb
from jupyter_db import orm

import nbformat

# from jupyter_db.visualise_sqla import visualise_sqla


# def test_sqla_visualise(tmp_path, file_regression):
#     # requires graphviz
#     db = jdb.JupyterDB(str(tmp_path), echo=False)
#     graph = visualise_sqla(db.declarative)
#     file_regression.check(graph.source, extension=".dot")


def test_populate(tmp_path, data_regression):
    db = jdb.JupyterDB(str(tmp_path), echo=False)
    doc = db.get_or_create_document(uri="path/to/doc")
    db.get_or_create_kernel(
        doc_uri=doc.uri, kernel_type="python", name="a", metadata={"timeout": 10}
    )
    db.get_or_create_kernel(doc_uri=doc.uri, kernel_type="python", name="b")
    # default is to add to the last kernel added to the document
    db.add_code_cell("a = 1", doc.uri, metadata={"timeout": 20})
    db.add_code_cell("b = 2", doc.uri, kernel_name="a")
    db.add_code_cell("c = 3", doc.uri, name="d")
    final_db = db.to_dict(drop_columns=("created_at", "updated_at"))
    data_regression.check(final_db)
    # remove document and all related kernels / code cells
    db.remove_document(uri="path/to/doc")
    assert [v for v in db.to_dict().values() if v] == []


def test_get_full_notebook(tmp_path, data_regression):
    db = jdb.JupyterDB(str(tmp_path), echo=False)
    doc = db.get_or_create_document(uri="path/to/doc")
    kernel = db.get_or_create_kernel(doc_uri=doc.uri, kernel_type="python")
    code_cell = db.add_code_cell("a = 1", doc.uri, metadata={"timeout": 20})
    with db.context_session() as session:
        session.add(code_cell)
        code_cell.execution = orm.OrmCellExecution()
        display = orm.OrmOutputDisplay(order=3, meta_data={"a": 1})
        display.data = {
            "text/html": orm.OrmMimeBundle(mimetype="text/html", source="<a>text<a\\>")
        }
        code_cell.execution.outputs = [
            orm.OrmOutputStream(order=0, name="stdout", text="abc"),
            orm.OrmOutputStream(order=1, name="stderr", text="abc"),
            orm.OrmOutputError(
                order=2, ename="ValueError", evalue="msg", traceback=["a", "b"]
            ),
            display,
        ]
    notebook = db.get_notebook(kernel.pk)
    data_regression.check(json.loads(nbformat.writes(notebook)))
