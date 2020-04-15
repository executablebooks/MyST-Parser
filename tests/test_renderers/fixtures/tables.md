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
                        <paragraph>
                            a
                    <entry>
                        <paragraph>
                            b
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            1
                    <entry>
                        <paragraph>
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
                        <paragraph>
                            a
                    <entry classes="text-align:center">
                        <paragraph>
                            b
                    <entry classes="text-align:right">
                        <paragraph>
                            c
            <tbody>
                <row>
                    <entry classes="text-align:left">
                        <paragraph>
                            1
                    <entry classes="text-align:center">
                        <paragraph>
                            2
                    <entry classes="text-align:right">
                        <paragraph>
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
                        <paragraph>
                            <emphasis>
                                a
                    <entry>
                        <paragraph>
                            <strong>
                                <emphasis>
                                    b
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            <math>
                                1
                    <entry>
                        <paragraph>
                            <subscript>
                                x
.

--------------------------
External links:
.
a|b
|-|-|
[link-a](https://www.google.com/)|[link-b](https://www.python.org/)
.
<document source="notset">
    <table classes="colwidths-auto">
        <tgroup cols="2">
            <colspec colwidth="50.0">
            <colspec colwidth="50.0">
            <thead>
                <row>
                    <entry>
                        <paragraph>
                            a
                    <entry>
                        <paragraph>
                            b
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            <reference refuri="https://www.google.com/">
                                link-a
                    <entry>
                        <paragraph>
                            <reference refuri="https://www.python.org/">
                                link-b
.