#!/usr/bin/env python3
"""Script to convert package setup to myst-docutils."""
import configparser
import io
import sys


def modify_setup_cfg(content: str) -> str:
    """Modify setup.cfg."""
    cfg = configparser.ConfigParser()
    cfg.read_string(content)
    # change name of package
    cfg.set("metadata", "name", "myst-docutils")
    # move dependency on docutils and sphinx to extra
    install_requires = []
    sphinx_extra = [""]
    for line in cfg.get("options", "install_requires").splitlines():
        if line.startswith("docutils"):
            sphinx_extra.append(line)
        elif line.startswith("sphinx"):
            sphinx_extra.append(line)
        else:
            install_requires.append(line)
    cfg.set("options", "install_requires", "\n".join(install_requires))
    cfg.set("options.extras_require", "sphinx", "\n".join(sphinx_extra))

    stream = io.StringIO()
    cfg.write(stream)
    return stream.getvalue()


def modify_readme(content: str) -> str:
    """Modify README.md."""
    content = content.replace(
        "# MyST-Parser",
        "# MyST-Parser\n\nNote: myst-docutils is identical to myst-parser, "
        "but without installation requirements on sphinx",
    )
    content = content.replace("myst-parser", "myst-docutils")
    content = content.replace("myst-docutils.readthedocs", "myst-parser.readthedocs")
    content = content.replace(
        "readthedocs.org/projects/myst-docutils", "readthedocs.org/projects/myst-parser"
    )
    return content


if __name__ == "__main__":
    setup_path = sys.argv[1]
    readme_path = sys.argv[2]
    with open(setup_path, "r") as f:
        content = f.read()
    content = modify_setup_cfg(content)
    with open(setup_path, "w") as f:
        f.write(content)
    with open(readme_path, "r") as f:
        content = f.read()
    content = modify_readme(content)
    with open(readme_path, "w") as f:
        f.write(content)
