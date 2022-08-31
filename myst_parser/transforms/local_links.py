from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING

from docutils import nodes
from docutils.transforms import Transform

from myst_parser._compat import findall
from myst_parser.warnings import MystWarnings

if TYPE_CHECKING:
    from sphinx.environment import BuildEnvironment


class MystLocalLink(nodes.Element):
    """A node for a link to a fragment in a Markdown document."""


@dataclass
class MystLocalTarget:
    """A reference target within a document."""

    name: str
    """The user facing name of the target"""
    id: str
    """The internal id of the target"""
    line: int | None
    """The line number of the target"""
    text: str | None = None
    """For use if no explicit text is given by the reference, e.g. the section title"""


class MdDocumentLinks(Transform):
    """Replace markdown links [text](#ref "title").

    When matching to a
    """

    default_priority = 880  # same as sphinx doctree-read even / std domain process_docs

    def apply(self):
        # import here, to avoid import loop
        from myst_parser.mdit_to_docutils.base import create_warning

        # mapping of name to target
        local_targets: dict[str, MystLocalTarget] = {}
        local_nodes: dict[str, nodes.Element] = {}

        # gather explicit target names
        # this mirrors the logic in `sphinx.domains.std.StandardDomain.process_doc`,
        # but here we want to store all specific to the docname
        for name, explicit in self.document.nametypes.items():
            if not explicit:
                continue
            labelid = self.document.nameids[name]
            if labelid is None:
                continue
            node = self.document.ids[labelid]
            if isinstance(node, nodes.target) and "refid" in node:
                # indirect hyperlink targets
                node = self.document.ids.get(node["refid"])
                labelid = node["names"][0]
            if (
                node.tagname == "footnote"
                or "refuri" in node
                or node.tagname.startswith("desc_")
            ):
                continue

            local_targets[name] = MystLocalTarget(name, labelid, node.line)
            local_nodes[name] = node

        # gather heading anchors
        for node in findall(self.document)():
            try:
                anchor_name = node.get("anchor_id")
            except AttributeError:
                anchor_name = None
            if anchor_name is None:
                continue
            if anchor_name in local_targets:
                # the anchor id may have already been set, if a target has the same name
                # TODO this check will still raise a warning,
                # if the section has been "promoted" to a doctitle or subtitle
                if local_nodes[anchor_name] is not node:
                    msg = f"skipping anchor with duplicate name {anchor_name!r}"
                    if local_targets[anchor_name].line:
                        msg += (
                            f", already set at line {local_targets[anchor_name].line}"
                        )
                    create_warning(
                        self.document,
                        msg,
                        MystWarnings.ANCHOR_DUPE,
                        line=node.line,
                    )
                continue

            anchor_id = anchor_name
            if anchor_name not in node["ids"]:
                index = 1
                while anchor_id in self.document.ids:
                    anchor_id += f"_{index}"
                    index += 1
                node["ids"].insert(0, anchor_id)

            local_targets[anchor_name] = MystLocalTarget(
                anchor_name, anchor_id, node.line
            )
            local_nodes[anchor_name] = node

        for name, node in local_nodes.items():
            if node.children and isinstance(node.children[0], nodes.title):
                local_targets[name].text = node.children[0].astext()

        # resolve local links
        for node in findall(self.document)(MystLocalLink):
            target = local_targets.get(node["refname"])
            if not target:
                create_warning(
                    self.document,
                    f"unknown link name {node['refname']!r}",
                    MystWarnings.REF_MISSING,
                    line=node.line,
                )
                # TODO what to do now? allow for children to remain? use external reference?
                # append the warning to the parent node?
                node.parent.remove(node)
            else:
                reference = nodes.reference(refid=target.id, internal=True)
                inner_node = nodes.inline("", "", classes=["std", "std-ref"])
                reference += inner_node
                inner_node.children = node.children
                if not inner_node.children:
                    if target.text:
                        inner_node.children = [nodes.Text(target.text)]
                    else:
                        create_warning(
                            self.document,
                            "empty link text",
                            MystWarnings.REF_EMPTY,
                            line=node.line,
                        )
                if node["classes"]:
                    reference["classes"].extend(node["classes"])
                if "title" in node:
                    reference["reftitle"] = node["title"]
                node.parent.replace(node, reference)

        # if using sphinx, then save local links to the environment,
        # for use by inter-document link resolution
        env: None | BuildEnvironment = getattr(self.document.settings, "env", None)
        if env is not None:
            env.metadata[env.docname]["myst_local_targets"] = {
                k: asdict(v) for k, v in local_targets.items()
            }
