from html.parser import HTMLParser
from docutils import nodes

from docutils.parsers.rst import directives


class ExitImageParse(Exception):
    pass


def align(argument):
    return directives.choice(argument, ("left", "center", "right"))


def make_error(document, error_msg, text, line_number):
    return document.reporter.error(
        "<img> conversion: {}".format(error_msg),
        nodes.literal_block(text, text),
        line=line_number,
    )


class HTMLImgParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self._attrs = dict(attrs)
        raise ExitImageParse()

    def parse(self, text: str, document: nodes.document, line_number: int):
        self.reset()
        self._attrs = None
        try:
            self.feed(text)
        except ExitImageParse:
            pass
        if self._attrs is None:
            return

        # TODO check for preceding text?

        if "src" not in self._attrs:
            return make_error(document, "missing src attribute", text, line_number)

        options = {}
        for name, key, spec in [
            ("src", "uri", directives.uri),
            ("class", "classes", directives.class_option),
            ("alt", "alt", directives.unchanged),
            ("height", "height", directives.length_or_unitless),
            ("width", "width", directives.length_or_percentage_or_unitless),
            ("align", "align", align)
            # note: docutils also has scale and target
        ]:
            if name in self._attrs:
                value = self._attrs[name]
                try:
                    options[key] = spec(value)
                except (ValueError, TypeError) as error:
                    error_msg = "Invalid attribute: (key: '{}'; value: {})\n{}".format(
                        name, value, error
                    )
                    return make_error(document, error_msg, text, line_number)

        node = nodes.image(text, **options)
        if "name" in self._attrs:
            name = nodes.fully_normalize_name(self._attrs["name"])
            node["names"].append(name)
            document.note_explicit_target(node, node)

        return node
