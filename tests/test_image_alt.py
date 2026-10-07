"""Image alt text keeps CommonMark escapes and entities."""

from docutils.core import publish_parts

from myst_parser.parsers.docutils_ import Parser


def _html(source: str) -> str:
    return publish_parts(source, parser=Parser(), writer_name="html5")["body"].strip()


def test_image_alt_keeps_escapes_and_entities():
    """Escapes and entities inside an image alt are not dropped.

    markdown-it-py represents them as ``text_special`` tokens with no children.
    Reading only ``text`` tokens used to drop the character
    (executablebooks/MyST-Parser#1210). The same source in a link already
    rendered the character.
    """
    assert _html(r"![a \* b](x.png)") == '<p><img alt="a * b" src="x.png" /></p>'
    assert _html("![a &amp; b](x.png)") == '<p><img alt="a &amp; b" src="x.png" /></p>'
    assert (
        _html(r"![C:\Python26](x.png)")
        == '<p><img alt="C:\\Python26" src="x.png" /></p>'
    )
    assert (
        _html(r"[a \* b &amp; c](https://example.com)")
        == '<p><a class="reference external" href="https://example.com">'
        "a * b &amp; c</a></p>"
    )
