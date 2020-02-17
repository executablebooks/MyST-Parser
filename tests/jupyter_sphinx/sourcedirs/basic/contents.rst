.. jupyter-kernel:: python3
    :allow_errors:

.. jupyter-exec::
    :timeout: 20
    :show-code:

    print("x")
    a = 1
    a

.. jupyter-view::

.. jupyter-exec::

    raise ValueError("failed")

.. jupyter-view::

    This is a *caption*

.. jupyter-exec::

    from IPython import display
    from base64 import b64decode
    display.Image(b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    ))

.. jupyter-view::
