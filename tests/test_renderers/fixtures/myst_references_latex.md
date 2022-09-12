doc-target
.
[](index.md)
.
\phantomsection\label{\detokenize{index::doc}}
\sphinxstepscope
\sphinxAtStartPar
{\hyperref[\detokenize{index::doc}]{\sphinxcrossref{Main}}}
.

section-target
.
(ref)=
# title
[](#ref)
.
\phantomsection\label{\detokenize{index::doc}}
\sphinxstepscope
\chapter{title}
\label{\detokenize{test:title}}\label{\detokenize{test:ref}}\label{\detokenize{test::doc}}
\sphinxAtStartPar
{\hyperref[\detokenize{test:ref}]{\sphinxcrossref{title}}}
.

math-label
.
```{math}
:label: abc
x = 1
```
[text](#abc)
.
\phantomsection\label{\detokenize{index::doc}}
\sphinxstepscope
\begin{equation}\label{equation:test:abc}
\begin{split}x = 1\end{split}
\end{equation}
\sphinxAtStartPar
{\hyperref[\detokenize{equation:test:abc}]{\sphinxcrossref{text}}}
.

glossary-term
.
```{glossary}
term
  definition
```
[](#term)
.
\phantomsection\label{\detokenize{index::doc}}
\sphinxstepscope
\begin{description}
\sphinxlineitem{term\index{term@\spxentry{term}|spxpagem}\phantomsection\label{\detokenize{test:term-term}}}
\sphinxAtStartPar
definition
\end{description}
\sphinxAtStartPar
{\hyperref[\detokenize{test:term-term}]{\sphinxcrossref{term}}}
.

ref_replacements [NUMBERED]
.
(sect)=
# Section
(subsect)=
## Subsection
[*{name}* {number}](#sect)
[*{name}* _ {number}](#subsect)
.
\phantomsection\label{\detokenize{index::doc}}
\sphinxstepscope
\chapter{Section}
\label{\detokenize{test:section}}\label{\detokenize{test:sect}}\label{\detokenize{test::doc}}
\section{Subsection}
\label{\detokenize{test:subsection}}\label{\detokenize{test:subsect}}
\sphinxAtStartPar
{\hyperref[\detokenize{test:sect}]{\sphinxcrossref{\sphinxstyleemphasis{\nameref{\detokenize{test:sect}}} \ref{\detokenize{test:sect}}}}}
{\hyperref[\detokenize{test:subsect}]{\sphinxcrossref{\sphinxstyleemphasis{\nameref{\detokenize{test:subsect}}} \_ \ref{\detokenize{test:subsect}}}}}
.

ref_replacements_math [NUMBERED]
.
# Section
## Subsection

```{math}
:label: eq1
x = 1
```
[*{name}* {number}](#eq1)
.
\phantomsection\label{\detokenize{index::doc}}
\sphinxstepscope
\chapter{Section}
\label{\detokenize{test:section}}\label{\detokenize{test::doc}}
\section{Subsection}
\label{\detokenize{test:subsection}}\begin{equation}\label{equation:test:eq1}
\begin{split}x = 1\end{split}
\end{equation}
\sphinxAtStartPar
{\hyperref[\detokenize{equation:test:eq1}]{\sphinxcrossref{\sphinxstyleemphasis{\nameref{\detokenize{equation:test:eq1}}} \ref{\detokenize{equation:test:eq1}}}}}
.
