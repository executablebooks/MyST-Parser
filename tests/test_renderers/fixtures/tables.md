--------------------------
Simple:
.
a|b
-|-
1|2
.
<document source="notset">
    <table classes="colwidths-auto">
        <tgroup cols="2">
            <colspec colwidth="50.0">
            <colspec colwidth="50.0">
            <thead>
                <row>
                    <entry>
                        a
                    <entry>
                        b
            <tbody>
                <row>
                    <entry>
                        1
                    <entry>
                        2
.

--------------------------
Aligned:
.
a | b | c
:-|:-:| -:
1 | 2 | 3
.
<document source="notset">
    <table classes="colwidths-auto">
        <tgroup cols="3">
            <colspec colwidth="33.33">
            <colspec colwidth="33.33">
            <colspec colwidth="33.33">
            <thead>
                <row>
                    <entry classes="text-align:left">
                        a
                    <entry classes="text-align:center">
                        b
                    <entry classes="text-align:right">
                        c
            <tbody>
                <row>
                    <entry classes="text-align:left">
                        1
                    <entry classes="text-align:center">
                        2
                    <entry classes="text-align:right">
                        3
.

--------------------------
Nested syntax:
.
| *a* | __*b*__  |
| --- | -------- |
|$1$  | {sub}`x` |
.
<document source="notset">
    <table classes="colwidths-auto">
        <tgroup cols="2">
            <colspec colwidth="50.0">
            <colspec colwidth="50.0">
            <thead>
                <row>
                    <entry>
                        <emphasis>
                            a
                    <entry>
                        <strong>
                            <emphasis>
                                b
            <tbody>
                <row>
                    <entry>
                        <math>
                            1
                    <entry>
                        <subscript>
                            x
.