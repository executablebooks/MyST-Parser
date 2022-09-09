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
