from nbconvert.preprocessors.execute import executenb
from jupyter_client.kernelspec import get_kernel_spec, NoSuchKernel

from jupyter_db import JupyterDB


class ExecutionError(Exception):
    pass


def run_execution(jupyter_db: JupyterDB):
    for kernel in jupyter_db.get_kernels(return_executed=False):
        try:
            spec = get_kernel_spec(kernel.kernel_type)
        except NoSuchKernel as err:
            raise ExecutionError("Unable to find kernel type: {}".format(err))
        notebook = jupyter_db.get_notebook(kernel.pk, with_outputs=False)
        notebook.metadata.update(
            {
                "kernelspec": {
                    "display_name": spec.display_name,
                    "language": spec.language,
                    "name": kernel.kernel_type,
                }
            }
        )
        try:
            executenb(notebook, **kernel.meta_data)
        except Exception as err:
            raise ExecutionError("Notebook execution failed : {}".format(err))
        jupyter_db.add_outputs_from_nb(kernel.pk, notebook)
