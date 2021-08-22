from myst_parser.docutils_ import Parser
from myst_parser.docutils_renderer import make_document


def test_parser():
    parser = Parser()
    document = make_document()
    parser.parse("something", document)
    assert (
        document.pformat().strip()
        == '<document source="notset">\n    <paragraph>\n        something'
    )
