import html
from typing import Iterable, Optional
from urllib.parse import quote, urlparse


def escape_url(raw: str) -> str:
    """
    Escape urls to prevent code injection craziness. (Hopefully.)
    """
    return html.escape(quote(html.unescape(raw), safe="/#:()*?=%@+,&"))


def is_external_url(
    reference: str, known_url_schemes: Optional[Iterable[str]], match_fragment: bool
) -> bool:
    """Return if a reference should be recognised as an external URL.

    URLs are of the format: scheme://netloc/path;parameters?query#fragment

    This checks if there is a url scheme (e.g. 'https') and, if so,
    if the scheme is is the list of known_url_schemes (if supplied).

    :param known_url_schemes: e.g. ["http", "https", "mailto"]
        If None, match all schemes
    :param match_fragment: If True and a fragment found, then True will be returned,
        irrespective of a scheme match

    """
    url_check = urlparse(reference)
    if known_url_schemes is not None:
        scheme_known = url_check.scheme in known_url_schemes
    else:
        scheme_known = bool(url_check.scheme)
    return scheme_known or (match_fragment and url_check.fragment != "")
