import html
from urllib.parse import quote


def escape_url(raw):
    """
    Escape urls to prevent code injection craziness. (Hopefully.)
    """
    return html.escape(quote(html.unescape(raw), safe="/#:()*?=%@+,&"))


class visualize_ast(object):
    """Visualize a docutils AST in a Jupyter or text environment.

    Inputs
    ------
    ast : docutils.nodes.document
    """

    def __init__(self, ast):
        self.ast = ast

    def _ipython_display_(self):
        try:
            # Being lazy w/ imports since this is probably only used by a dev
            from IPython.display import JSON, display
            import xmltodict

            xmld = xmltodict.parse(self.ast.asdom().toxml())
            display(JSON(xmld))
        except ImportError:
            print("To pretty-display this object, install xmltodict\n---\n")
            print(self.ast.pformat())

    def __repr__(self):
        return self.ast.pformat()
