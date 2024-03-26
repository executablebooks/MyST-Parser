#!/usr/bin/env python3
"""Script to convert package setup to myst-docutils."""
import sys
from pathlib import Path

import tomlkit


def modify_toml(content: str) -> str:
    """Modify `pyproject.toml`."""
    doc = tomlkit.parse(content)

    # change name of package
    doc["project"]["name"] = "myst-docutils"

    # move dependency on docutils and sphinx to extra
    dependencies = []
    sphinx_extra = []
    for dep in doc["project"]["dependencies"]:
        if dep.startswith("docutils") or dep.startswith("sphinx"):
            sphinx_extra.append(dep)
        else:
            dependencies.append(dep)
    doc["project"]["dependencies"] = dependencies
    doc["project"]["optional-dependencies"]["sphinx"] = sphinx_extra

    return tomlkit.dumps(doc)


def modify_readme(content: str) -> str:
    """Modify README.md."""
    content = content.replace("myst-parser", "myst-docutils")
    content = content.replace(
        "# MyST-Parser",
        "# MyST-Parser\n\nNote: myst-docutils is identical to myst-parser, "
        "but without installation requirements on sphinx",
    )
    content = content.replace("myst-docutils.readthedocs", "myst-parser.readthedocs")
    content = content.replace(
        "readthedocs.org/projects/myst-docutils", "readthedocs.org/projects/myst-parser"
    )
    return content


if __name__ == "__main__":
    project_path = Path(sys.argv[1])
    content = project_path.read_text()
    content = modify_toml(content)
    project_path.write_text(content)

    readme_path = Path(sys.argv[2])
    content = readme_path.read_text()
    content = modify_readme(content)
    readme_path.write_text(content)
