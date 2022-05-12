Single Line:
.
\begin{equation} a \end{equation}
.
<document source="<src>/index.md">
    <target ids="equation-mock-uuid">
    <math_block classes="amsmath" docname="index" label="mock-uuid" nowrap="True" number="1" xml:space="preserve">
        \begin{equation} a \end{equation}
.

Multi Line:
.
\begin{equation}
a
\end{equation}
.
<document source="<src>/index.md">
    <target ids="equation-mock-uuid">
    <math_block classes="amsmath" docname="index" label="mock-uuid" nowrap="True" number="1" xml:space="preserve">
        \begin{equation}
        a
        \end{equation}
.

Multi Line no number:
.
\begin{equation*}
a
\end{equation*}
.
<document source="<src>/index.md">
    <math_block classes="amsmath" nowrap="True" number="True" xml:space="preserve">
        \begin{equation*}
        a
        \end{equation*}
.

In list:
.
- \begin{equation}
  a = 1
  \end{equation}
.
<document source="<src>/index.md">
    <bullet_list bullet="-">
        <list_item>
            <target ids="equation-mock-uuid">
            <math_block classes="amsmath" docname="index" label="mock-uuid" nowrap="True" number="1" xml:space="preserve">
                \begin{equation}
                  a = 1
                  \end{equation}
.
