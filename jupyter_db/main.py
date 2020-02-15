from contextlib import contextmanager
import pathlib
from sqlite3 import Connection as SQLite3Connection
from typing import Iterator, Optional

import sqlalchemy as sqla
from sqlalchemy.orm import sessionmaker, Session

import nbformat


from .orm import (  # noqa: F401
    OrmBase,
    OrmCellExecution,
    OrmCodeCell,
    OrmDocument,
    OrmKernel,
    OrmKernelInfo,
    OrmOutput,
    OrmOutputDisplay,
    OrmOutputError,
    OrmOutputExecute,
    OrmOutputStream,
    OrmMimeBundle,
)


@sqla.event.listens_for(sqla.engine.Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    """Enforce foreign key constraints, when using sqlite backend (off by default)"""
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


class JupyterDB:
    """A database cache for code kernels, cells and outputs."""

    def __init__(self, db_folder_path: str, db_file_name: str = "jupyter.db", **kwargs):
        self._db_path = (pathlib.Path(db_folder_path) / db_file_name).absolute()
        self._engine = sqla.create_engine(
            "sqlite:///{}".format(self._db_path), **kwargs
        )
        OrmBase.metadata.create_all(self._engine)
        self._session_factory = sessionmaker(bind=self._engine)

    @property
    def declarative(self) -> sqla.ext.declarative.DeclarativeMeta:
        return OrmBase

    def __getstate__(self):
        """For pickling instance."""
        state = self.__dict__.copy()
        state["_engine"] = None
        state["_session_factory"] = None
        return state

    def __setstate__(self, newstate):
        """For unpickling instance."""
        newstate["_engine"] = sqla.create_engine(
            "sqlite:///{}".format(newstate["_db_path"])
        )
        newstate["_session_factory"] = sessionmaker(bind=newstate["_engine"])
        self.__dict__.update(newstate)

    @contextmanager
    def context_session(self, *, session=None, final_commit=True) -> Iterator[Session]:
        """Provide a transactional scope around a series of operations."""
        if session is None:
            session = self._session_factory()
            close_on_exit = True
        else:
            close_on_exit = False
        try:
            yield session
            if final_commit:
                session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            if close_on_exit:
                session.close()

    def to_dict(self, *, drop_tables=(), drop_columns=()) -> dict:
        """Convert all database tables to json (for testing purposes)."""
        result = {}
        with self.context_session() as session:  # type: Session
            for name, entity in OrmBase.metadata.tables.items():
                if name in drop_tables:
                    continue
                drop_cols = (
                    drop_columns.get(name, ())
                    if isinstance(drop_columns, dict)
                    else drop_columns
                )
                result[name] = [
                    {k: v for k, v in r._asdict().items() if k not in drop_cols}
                    for r in session.query(entity)
                ]
        return result

    def get_or_create_document(
        self, uri: str, *, session: Optional[Session] = None
    ) -> OrmDocument:
        with self.context_session(
            session=session, final_commit=False
        ) as session:  # type: Session
            doc = session.query(OrmDocument).filter_by(uri=uri).one_or_none()
            if doc is None:
                doc = OrmDocument(uri=uri)
                session.add(doc)
                session.commit()
                session.refresh(doc)
            session.expunge(doc)
        return doc

    def remove_document(self, uri: str, *, session: Optional[Session] = None):
        """Remove a document and its associated kernels and code cells."""
        with self.context_session() as session:  # type: Session
            doc = session.query(OrmDocument).filter_by(uri=uri).one_or_none()
            if doc is None:
                return
            session.delete(doc)

    def get_or_create_kernel(
        self,
        doc_uri: int,
        kernel_type: str,
        *,
        name: Optional[str] = None,
        metadata: Optional[dict] = None,
        session: Optional[Session] = None,
    ) -> OrmKernel:
        with self.context_session(
            session=session, final_commit=False
        ) as session:  # type: Session
            doc = session.query(OrmDocument).filter_by(uri=doc_uri).one()
            kernel = (
                session.query(OrmKernel)
                .filter_by(doc_pk=doc.pk, kernel_type=kernel_type, name=name)
                .one_or_none()
            )
            if kernel is None:
                kernel = OrmKernel(
                    doc_pk=doc.pk,
                    doc_order=len(doc.kernels),
                    kernel_type=kernel_type,
                    name=name,
                    meta_data=metadata,
                )
                session.add(kernel)
                session.commit()
                session.refresh(kernel)
            session.expunge(kernel)
        return kernel

    def add_code_cell(
        self,
        source: str,
        doc_uri: str,
        *,
        name: Optional[str] = None,
        metadata: Optional[dict] = None,
        kernel_name: Optional[str] = None,
        session: Optional[Session] = None,
    ) -> OrmCodeCell:
        """Add a code cell.

        If kernel_name is None, add to last kernel added to doc
        """
        with self.context_session(
            session=session, final_commit=False
        ) as session:  # type: Session
            doc = session.query(OrmDocument).filter_by(uri=doc_uri).one()
            if kernel_name is None:
                kernel = doc.kernels[-1]
            else:
                kernel = session.query(OrmKernel).filter_by(name=kernel_name).one()
            code_cell = OrmCodeCell(
                source=source,
                name=name,
                meta_data=metadata,
                doc_pk=doc.pk,
                doc_order=len(doc.codecells),
                kernel_pk=kernel.pk,
                exec_order=len(kernel.codecells),
            )
            session.add(code_cell)
            session.commit()
            _ = code_cell.pk
            session.expunge(code_cell)
        return code_cell

    def get_code_cell(
        self, doc_uri, *, name: Optional[str] = None, session: Optional[Session] = None
    ) -> OrmCodeCell:
        with self.context_session(
            session=session, final_commit=False
        ) as session:  # type: Session
            if name is None:
                doc = session.query(OrmDocument).filter_by(uri=doc_uri).one()
                code_cell = doc.codecells[-1]
            else:
                code_cell = session.query(OrmCodeCell).filter_by(name=name).one()
            session.expunge(code_cell)
        return code_cell

    def get_notebook_cell(
        self, pk, *, with_outputs=True, session: Optional[Session] = None
    ) -> nbformat.NotebookNode:
        with self.context_session(
            session=session, final_commit=False
        ) as session:  # type: Session
            cell = session.query(OrmCodeCell).filter_by(pk=pk).one()
            nb_cell = cell.to_nbformat(with_outputs=with_outputs)
        return nb_cell

    def get_cell_language(self, pk, *, session: Optional[Session] = None):
        with self.context_session(
            session=session, final_commit=False
        ) as session:  # type: Session
            cell = session.query(OrmCodeCell).filter_by(pk=pk).one()
            # TODO error if not run?
            try:
                lexer = cell.kernel.info.data["language_info"]["pygments_lexer"]
            except Exception:
                lexer = cell.kernel.info.data["kernelspec"]["language"]
        return lexer

    def get_kernels(self, return_executed=False, *, session: Optional[Session] = None):
        """If not return_executed,
        only return kernels that have not been previously run.
        """
        with self.context_session(
            session=session, final_commit=False
        ) as session:  # type: Session
            kernels = []
            for kernel in session.query(OrmKernel).all():
                if return_executed or kernel.info is None:
                    session.expunge(kernel)
                    kernels.append(kernel)
        return kernels

    def get_notebook(
        self, kernel_pk: int, *, with_outputs=True, session: Optional[Session] = None
    ) -> nbformat.NotebookNode:
        with self.context_session(
            session=session, final_commit=False
        ) as session:  # type: Session
            kernel = session.query(OrmKernel).filter_by(pk=kernel_pk).one()
            return kernel.to_nbformat(with_outputs=with_outputs)

    def add_outputs_from_nb(
        self,
        kernel_pk: int,
        nb: nbformat.NotebookNode,
        *,
        session: Optional[Session] = None,
    ):
        with self.context_session(
            session=session, final_commit=True
        ) as session:  # type: Session
            kernel = session.query(OrmKernel).filter_by(pk=kernel_pk).one()
            if not len(nb.cells) == len(kernel.codecells):
                raise AssertionError("notebook has a different number of cells")
            kernel.info = OrmKernelInfo(
                data={
                    k: nb.metadata.get(k, {}) for k in ["kernelspec", "language_info"]
                }
            )
            for i, (nb_cell, orm_cell) in enumerate(zip(nb.cells, kernel.codecells)):
                orm_cell.execution = OrmCellExecution(execution_count=i)
                orm_outputs = [
                    OrmOutput.from_nbformat(output, j)
                    for j, output in enumerate(nb_cell.outputs)
                ]
                orm_cell.execution.outputs = orm_outputs
