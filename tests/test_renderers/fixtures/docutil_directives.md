--------------------------------
[attention] (`docutils.parsers.rst.directives.admonitions.Attention`):
.
```{attention}

a
```
.
<document source="notset">
    <attention>
        <paragraph>
            a
.

--------------------------------
[caution] (`docutils.parsers.rst.directives.admonitions.Caution`):
.
```{caution}

a
```
.
<document source="notset">
    <caution>
        <paragraph>
            a
.

--------------------------------
[danger] (`docutils.parsers.rst.directives.admonitions.Danger`):
.
```{danger}

a
```
.
<document source="notset">
    <danger>
        <paragraph>
            a
.

--------------------------------
[error] (`docutils.parsers.rst.directives.admonitions.Error`):
.
```{error}

a
```
.
<document source="notset">
    <error>
        <paragraph>
            a
.

--------------------------------
[important] (`docutils.parsers.rst.directives.admonitions.Important`):
.
```{important}

a
```
.
<document source="notset">
    <important>
        <paragraph>
            a
.

--------------------------------
[note] (`docutils.parsers.rst.directives.admonitions.Note`):
.
```{note}

a
```
.
<document source="notset">
    <note>
        <paragraph>
            a
.

--------------------------------
[tip] (`docutils.parsers.rst.directives.admonitions.Tip`):
.
```{tip}

a
```
.
<document source="notset">
    <tip>
        <paragraph>
            a
.

--------------------------------
[hint] (`docutils.parsers.rst.directives.admonitions.Hint`):
.
```{hint}

a
```
.
<document source="notset">
    <hint>
        <paragraph>
            a
.

--------------------------------
[warning] (`docutils.parsers.rst.directives.admonitions.Warning`):
.
```{warning}

a
```
.
<document source="notset">
    <warning>
        <paragraph>
            a
.

--------------------------------
[admonition] (`docutils.parsers.rst.directives.admonitions.Admonition`):
.
```{admonition} myclass

a
```
.
<document source="notset">
    <admonition classes="admonition-myclass">
        <title>
            myclass
        <paragraph>
            a
.

--------------------------------
[sidebar] (`docutils.parsers.rst.directives.body.Sidebar`):
.
```{sidebar} sidebar title

a
```
.
<document source="notset">
    <sidebar>
        <title>
            sidebar title
        <paragraph>
            a
.

--------------------------------
[topic] (`docutils.parsers.rst.directives.body.Topic`):
.
```{topic} Topic Title

a
```
.
<document source="notset">
    <topic>
        <title>
            Topic Title
        <paragraph>
            a
.

--------------------------------
[line-block] (`docutils.parsers.rst.directives.body.LineBlock`) SKIP: MockingError: MockState has not yet implemented attribute 'nest_line_block_lines'
.
```{line-block}


```
.
<document source="notset">
.

--------------------------------
[parsed-literal] (`docutils.parsers.rst.directives.body.ParsedLiteral`):
.
```{parsed-literal}

a
```
.
<document source="notset">
    <literal_block xml:space="preserve">
        a
.

--------------------------------
[rubric] (`docutils.parsers.rst.directives.body.Rubric`):
.
```{rubric} Rubric Title
```
.
<document source="notset">
    <rubric>
        Rubric Title
.

--------------------------------
[epigraph] (`docutils.parsers.rst.directives.body.Epigraph`):
.
```{epigraph}

a

-- attribution
```
.
<document source="notset">
    <block_quote classes="epigraph">
        <paragraph>
            a
        <attribution>
            attribution
.

--------------------------------
[highlights] (`docutils.parsers.rst.directives.body.Highlights`):
.
```{highlights}

a

-- attribution
```
.
<document source="notset">
    <block_quote classes="highlights">
        <paragraph>
            a
        <attribution>
            attribution
.

--------------------------------
[pull-quote] (`docutils.parsers.rst.directives.body.PullQuote`):
.
```{pull-quote}

a

-- attribution
```
.
<document source="notset">
    <block_quote classes="pull-quote">
        <paragraph>
            a
        <attribution>
            attribution
.

--------------------------------
[compound] (`docutils.parsers.rst.directives.body.Compound`):
.
```{compound}

a
```
.
<document source="notset">
    <compound>
        <paragraph>
            a
.

--------------------------------
[container] (`docutils.parsers.rst.directives.body.Container`):
.
```{container}

a
```
.
<document source="notset">
    <container>
        <paragraph>
            a
.

--------------------------------
[image] (`docutils.parsers.rst.directives.images.Image`):
.
```{image} path/to/image
:alt: abc
:name: name
```
.
<document source="notset">
    <image alt="abc" ids="name" names="name" uri="path/to/image">
.

--------------------------------
[raw] (`docutils.parsers.rst.directives.misc.Raw`):
.
```{raw} raw

a
```
.
<document source="notset">
    <raw format="raw" xml:space="preserve">
        a
.

--------------------------------
[class] (`docutils.parsers.rst.directives.misc.Class`):
.
```{class} myclass

a
```
.
<document source="notset">
    <paragraph classes="myclass">
        a
.

--------------------------------
[role] (`docutils.parsers.rst.directives.misc.Role`) + raw (`docutils.parsers.rst.roles.raw_role`):
.
```{role} raw-latex(raw)
:format: latex
```

{raw-latex}`\tag{content}`
.
<document source="notset">
    <paragraph>
        <raw classes="raw-latex" format="latex" xml:space="preserve">
            \tag{content}
.

--------------------------------
[title] (`docutils.parsers.rst.directives.misc.Title`):
.
```{title} title
```
.
<document source="notset" title="title">
.

--------------------------------
[restructuredtext-test-directive] (`docutils.parsers.rst.directives.misc.TestDirective`):
.
```{restructuredtext-test-directive}
```
.
<document source="notset">
    <system_message level="1" line="1" source="notset" type="INFO">
        <paragraph>
            Directive processed. Type="restructuredtext-test-directive", arguments=[], options={}, content: None
.

--------------------------------
[contents] (`docutils.parsers.rst.directives.parts.Contents`):
.
```{contents} Contents
```
.
<document source="notset">
    <topic classes="contents" ids="contents" names="contents">
        <title>
            Contents
        <pending>
            .. internal attributes:
                 .transform: docutils.transforms.parts.Contents
                 .details:
.

--------------------------------
[sectnum] (`docutils.parsers.rst.directives.parts.Sectnum`):
.
```{sectnum}
```
.
<document source="notset">
    <pending>
        .. internal attributes:
             .transform: docutils.transforms.parts.SectNum
             .details:
.

--------------------------------
[header] (`docutils.parsers.rst.directives.parts.Header`):
.
```{header}

a
```
.
<document source="notset">
    <decoration>
        <header>
            <paragraph>
                a
.

--------------------------------
[footer] (`docutils.parsers.rst.directives.parts.Footer`):
.
```{footer}

a
```
.
<document source="notset">
    <decoration>
        <footer>
            <paragraph>
                a
.

--------------------------------
[target-notes] (`docutils.parsers.rst.directives.references.TargetNotes`):
.
```{target-notes}
```
.
<document source="notset">
    <pending>
        .. internal attributes:
             .transform: docutils.transforms.references.TargetNotes
             .details:
.
