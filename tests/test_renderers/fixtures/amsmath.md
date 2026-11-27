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

With label:
.
\begin{equation}
a = 1 \label{eq:my-label}
\end{equation}
.
<document source="<src>/index.md">
    <target ids="equation-eq-my-label">
    <math_block classes="amsmath" docname="index" label="eq:my-label" nowrap="True" number="1" xml:space="preserve">
        \begin{equation}
        a = 1 \label{eq:my-label}
        \end{equation}
.

With label and reference:
.
\begin{align}
\label{eq1}
a &= 1 \\
b &= 2
\end{align}

{eq}`eq1`
.
<document source="<src>/index.md">
    <target ids="equation-eq1">
    <math_block classes="amsmath" docname="index" label="eq1" nowrap="True" number="1" xml:space="preserve">
        \begin{align}
        \label{eq1}
        a &= 1 \\
        b &= 2
        \end{align}
    <paragraph>
        <pending_xref refdoc="index" refdomain="math" refexplicit="False" reftarget="eq1" reftype="eq" refwarn="True">
            <literal classes="xref eq">
                eq1
.

Label in comment is ignored:
.
\begin{equation}
a = 1 % \label{eq1}
\end{equation}
.
<document source="<src>/index.md">
    <target ids="equation-mock-uuid">
    <math_block classes="amsmath" docname="index" label="mock-uuid" nowrap="True" number="1" xml:space="preserve">
        \begin{equation}
        a = 1 % \label{eq1}
        \end{equation}
.

Label after escaped percent:
.
\begin{equation}
a = 1\% \label{eq1}
\end{equation}
.
<document source="<src>/index.md">
    <target ids="equation-eq1">
    <math_block classes="amsmath" docname="index" label="eq1" nowrap="True" number="1" xml:space="preserve">
        \begin{equation}
        a = 1\% \label{eq1}
        \end{equation}
.

Label in no number environment is ignored:
.
\begin{equation*}
a = 1 \label{eq1}
\end{equation*}
.
<document source="<src>/index.md">
    <math_block classes="amsmath" nowrap="True" number="True" xml:space="preserve">
        \begin{equation*}
        a = 1 \label{eq1}
        \end{equation*}
.

Multiple labels:
.
\begin{align}
a &= 1 \label{eq1} \\
b &= 2 \label{eq2}
\end{align}
.
<document source="<src>/index.md">
    <system_message level="2" line="1" source="<src>/index.md" type="WARNING">
        <paragraph>
            Only one \label is supported per amsmath environment, ignoring: eq1, eq2 [myst.math_label]
    <target ids="equation-mock-uuid">
    <math_block classes="amsmath" docname="index" label="mock-uuid" nowrap="True" number="1" xml:space="preserve">
        \begin{align}
        a &= 1 \label{eq1} \\
        b &= 2 \label{eq2}
        \end{align}

<src>/index.md:1: WARNING: Only one \label is supported per amsmath environment, ignoring: eq1, eq2 [myst.math_label]
.
