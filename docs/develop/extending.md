(develop/extending)=

# Extending the parser: rendering generated content

Some Sphinx/docutils directives do not just wrap their literal content, but
*generate* new content to render -- for example an included file, or markup
produced from a template.  This page describes the supported API for doing that
from a directive under MyST, so that the generated content is rendered as MyST
Markdown and its warnings and nodes are attributed to the right source.

:::{important}
Content rendered through these APIs is parsed as **MyST Markdown**, not
reStructuredText.  A directive that generates rST should wrap it in an
[`{eval-rst}`](syntax/directives/parsing) block instead.
:::

## Reaching the renderer from a directive

When MyST runs a directive it passes mock ``state`` and ``state_machine``
objects (rather than the docutils reStructuredText ones).  Both expose the
active MyST renderer through a read-only ``renderer`` property, which is the
supported entry point for the APIs below:

```python
from docutils.parsers.rst import Directive


class MyDirective(Directive):
    has_content = False

    def run(self):
        renderer = self.state.renderer  # or self.state_machine.renderer
        ...
        return []
```

See {py:obj}`myst_parser.mocking.MockState.renderer` and
{py:obj}`myst_parser.mocking.MockStateMachine.renderer`.

## Rendering generated text

{py:meth}`myst_parser.mdit_to_docutils.base.DocutilsRenderer.nested_render_text`
renders a string of MyST at the current position (appending to the current
node):

```python
self.state.renderer.nested_render_text(text, lineno)
```

The ``lineno`` argument is a **0-based line shift** added to every rendered
node's line: it establishes the *line-space* of ``text``.  There are two common
choices:

- **Document-relative content** -- pass the directive's ``content_offset`` (see
  [below](content-offset)), so the generated lines map onto the document.
- **File- or template-relative content** -- pass ``0``, so line ``N`` of the
  generated text is reported as line ``N`` (of that file/template, when combined
  with ``source`` below).

For example, generated text whose warnings should read as lines ``1, 2, 3, …``
of a template is rendered with ``lineno=0``.

### Attributing to a source

Pass ``source`` to attribute both the rendered nodes' ``source`` and any
warnings emitted during the render to a specific path (typically the absolute
path of the file or template the text came from), rather than the containing
document:

```python
self.state.renderer.nested_render_text(template_output, 0, source="/abs/template.j2")
```

A warning on the first line of ``template_output`` is then reported as
``/abs/template.j2:1`` in both docutils and Sphinx builds, and the resulting
nodes carry ``source="/abs/template.j2"``.  The override is restored when the
render finishes (even on error) and nests correctly, so a source render may
itself contain further source renders -- this is exactly how nested
``{include}`` directives attribute each file.

:::{note}
In Sphinx the location is passed to the logger as a ``"source:line"`` *string*.
This is deliberate: Sphinx passes a colon-containing string through verbatim,
whereas a plain path would be resolved against the project via ``doc2path``.
:::

## Inserting text at the directive's position

{py:meth}`myst_parser.mocking.MockStateMachine.insert_input` mirrors the
signature of docutils' ``RSTStateMachine.insert_input``, so directives written
for docutils keep working:

```python
self.state_machine.insert_input(generated_lines, source="/abs/gen.txt")
```

Two behavioural differences are worth knowing:

- the lines are parsed as **MyST Markdown**, not reStructuredText;
- they are rendered *immediately* into the current node -- appearing **before**
  any nodes the directive itself returns -- rather than being spliced back into
  the input stream.  For the common ``return []`` pattern the outcome is
  identical to docutils.

Without ``source`` the text is rendered in the document's own line-space, just
after the directive.

(content-offset)=
## What ``content_offset`` means

A directive's ``self.content_offset`` is **document-relative**: it is the
0-based absolute line of the directive's first content line (equivalently, its
1-based document line minus one), exactly as docutils' own reStructuredText
parser provides.  The standard idiom therefore reports true document lines:

```python
# the Nth (1-based) content line is document line content_offset + N
self.state_machine.reporter.warning("...", line=self.content_offset + n)
```

and each entry of ``self.content.items`` carries the absolute document line of
its line.  A plain nested parse of the content needs nothing special:

```python
self.state.nested_parse(self.content, self.content_offset, node)
```

## Documented limitations

- **Deferred, document-level warnings** are *not* covered by a render-scoped
  ``source``.  For instance, a duplicate Markdown reference definition is
  reported at the end of the whole-document render, so it attributes to the
  containing document (with the in-file line) even when the definition came from
  an included file.
- **Inline tokens carry no per-line maps**, so a warning about inline content is
  attributed to the line of its containing block, not the exact inline position.

## API reference

- {py:obj}`myst_parser.mocking.MockState.renderer` /
  {py:obj}`myst_parser.mocking.MockStateMachine.renderer`
- {py:meth}`myst_parser.mdit_to_docutils.base.DocutilsRenderer.nested_render_text`
- {py:meth}`myst_parser.mocking.MockStateMachine.insert_input`
- {py:func}`myst_parser.warnings_.create_warning`
