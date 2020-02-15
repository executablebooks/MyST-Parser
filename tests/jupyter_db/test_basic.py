# from sqlalchemy.orm import Session

from jupyter_db import main as jdb

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
