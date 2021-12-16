--------------------------------
Single Line:
.
\begin{equation} a \end{equation}
.
<document source="notset">
    <target ids="equation-mock-uuid">
    <math_block classes="amsmath" docname="mock_docname" label="mock-uuid" nowrap="True" number="1" xml:space="preserve">
        \begin{equation} a \end{equation}
.

--------------------------------
Multi Line:
.
\begin{equation}
a
\end{equation}
.
<document source="notset">
    <target ids="equation-mock-uuid">
    <math_block classes="amsmath" docname="mock_docname" label="mock-uuid" nowrap="True" number="1" xml:space="preserve">
        \begin{equation}
        a
        \end{equation}
.

--------------------------------
Multi Line no number:
.
\begin{equation*}
a
\end{equation*}
.
<document source="notset">
    <math_block classes="amsmath" nowrap="True" number="True" xml:space="preserve">
        \begin{equation*}
        a
        \end{equation*}
.

--------------------------------
In list:
.
- \begin{equation}
  a = 1
  \end{equation}
.
<document source="notset">
    <bullet_list bullet="-">
        <list_item>
            <target ids="equation-mock-uuid">
            <math_block classes="amsmath" docname="mock_docname" label="mock-uuid" nowrap="True" number="1" xml:space="preserve">
                \begin{equation}
                  a = 1
                  \end{equation}
.
