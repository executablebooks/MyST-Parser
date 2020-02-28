import pathlib
import tempfile

from myst_parser.cli import benchmark


def test_benchmark():
    with tempfile.TemporaryDirectory() as tempdir:
        path = pathlib.Path(tempdir).joinpath("test.md")
        path.write_text("a b c")
        assert benchmark.main(["-n", "1", "-p", "myst_parser:html", str(path)])
