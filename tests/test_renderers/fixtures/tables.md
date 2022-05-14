Simple:
.
a|b
-|-
1|2
.
<document source="<src>/index.md">
    <table classes="colwidths-auto">
        <tgroup cols="2">
            <colspec colwidth="50">
            <colspec colwidth="50">
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

Header only:
.
| abc | def |
| --- | --- |
.
<document source="<src>/index.md">
    <table classes="colwidths-auto">
        <tgroup cols="2">
            <colspec colwidth="50">
            <colspec colwidth="50">
            <thead>
                <row>
                    <entry>
                        <paragraph>
                            abc
                    <entry>
                        <paragraph>
                            def
.

Aligned:
.
a | b | c
:-|:-:| -:
1 | 2 | 3
.
<document source="<src>/index.md">
    <table classes="colwidths-auto">
        <tgroup cols="3">
            <colspec colwidth="33">
            <colspec colwidth="33">
            <colspec colwidth="33">
            <thead>
                <row>
                    <entry classes="text-left">
                        <paragraph>
                            a
                    <entry classes="text-center">
                        <paragraph>
                            b
                    <entry classes="text-right">
                        <paragraph>
                            c
            <tbody>
                <row>
                    <entry classes="text-left">
                        <paragraph>
                            1
                    <entry classes="text-center">
                        <paragraph>
                            2
                    <entry classes="text-right">
                        <paragraph>
                            3
.

Nested syntax:
.
| *a* | __*b*__  |
| --- | -------- |
|c  | {sub}`x` |
.
<document source="<src>/index.md">
    <table classes="colwidths-auto">
        <tgroup cols="2">
            <colspec colwidth="50">
            <colspec colwidth="50">
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
                            c
                    <entry>
                        <paragraph>
                            <subscript>
                                x
.

External links:
.
a|b
|-|-|
[link-a](https://www.google.com/)|[link-b](https://www.python.org/)
.
<document source="<src>/index.md">
    <table classes="colwidths-auto">
        <tgroup cols="2">
            <colspec colwidth="50">
            <colspec colwidth="50">
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
