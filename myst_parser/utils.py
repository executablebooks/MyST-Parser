import html
from urllib.parse import quote


def escape_url(raw):
    """
    Escape urls to prevent code injection craziness. (Hopefully.)
    """
    return html.escape(quote(html.unescape(raw), safe="/#:()*?=%@+,&"))
