"""Tests for merging file-level topmatter into the global config."""

import io

import pytest
from docutils.core import publish_doctree

from myst_parser.config.main import MdParserConfig, merge_file_level
from myst_parser.parsers.docutils_ import Parser
from myst_parser.warnings_ import MystWarnings


def merge(topmatter):
    """Merge topmatter into a default config, returning (config, warnings)."""
    warnings: list[tuple[MystWarnings, str]] = []
    config = merge_file_level(
        MdParserConfig(), topmatter, lambda kind, msg: warnings.append((kind, msg))
    )
    return config, [msg for _kind, msg in warnings]


class TestValidatorNormalisation:
    """A validator that normalises its value must have the last word.

    ``validate_field`` was called *before* ``setattr``, so a validator that
    resolved or converted the value and wrote it back on the instance had that
    result immediately overwritten with the raw topmatter value.
    """

    def test_a_sequence_is_stored_as_the_set_the_field_holds(self):
        """`check_fence_as_directive` converts to a set; the raw value is a list.

        Downstream code does set operations on this field, so a list here is a
        wrong type, not merely a different one.
        """
        config, warnings = merge({"myst": {"fence_as_directive": ["mermaid"]}})
        assert warnings == []
        assert isinstance(config.fence_as_directive, set)
        assert config.fence_as_directive == {"mermaid"}

    def test_the_global_value_is_a_set_too(self):
        """Pins the invariant the test above is protecting."""
        assert isinstance(MdParserConfig().fence_as_directive, set)


class TestGlobalOnlyFields:
    """``global_only`` metadata must actually be enforced.

    It was declared on five fields and checked nowhere, so topmatter could set
    them. For ``heading_slug_func`` that produced
    ``'str' object is not callable`` for every heading, because the field then
    held the preset *name* rather than the function it names.
    """

    @pytest.mark.parametrize(
        "name,value",
        [
            ("heading_slug_func", "github"),
            ("update_mathjax", False),
            ("mathjax_classes", "tex2jax_process"),
            ("suppress_warnings", ["myst.xref_missing"]),
            ("inventories", {"x": ["https://example.com", None]}),
        ],
    )
    def test_a_global_only_field_is_rejected(self, name, value):
        config, warnings = merge({"myst": {name: value}})
        assert warnings == [
            f"'{name}' is a global-only config and cannot be set in topmatter"
        ]
        assert getattr(config, name) == getattr(MdParserConfig(), name)

    def test_the_rejected_field_keeps_the_global_value(self):
        """Not just unchanged from the default -- unchanged from the global."""
        warnings: list[str] = []
        global_config = MdParserConfig(heading_slug_func=str.upper)
        config = merge_file_level(
            global_config,
            {"myst": {"heading_slug_func": "github"}},
            lambda kind, msg: warnings.append(msg),
        )
        assert config.heading_slug_func is str.upper
        assert len(warnings) == 1

    def test_a_non_global_field_alongside_one_is_still_applied(self):
        """Rejecting one key must not abandon the rest of the topmatter."""
        config, warnings = merge(
            {
                "myst": {
                    "heading_slug_func": "github",
                    "enable_extensions": ["dollarmath"],
                }
            }
        )
        assert len(warnings) == 1
        assert "dollarmath" in config.enable_extensions


class TestInvalidValues:
    """An invalid value must be reported and must not be half-applied."""

    def test_an_invalid_value_is_rolled_back(self):
        """The value is now assigned before validation, so it has to be undone.

        Otherwise a rejected value would be reported *and* kept.
        """
        config, warnings = merge({"myst": {"fence_as_directive": "not-a-sequence"}})
        assert len(warnings) == 1
        assert config.fence_as_directive == MdParserConfig().fence_as_directive

    def test_an_invalid_value_rolls_back_to_the_global_not_the_default(self):
        warnings: list[str] = []
        global_config = MdParserConfig(fence_as_directive={"mermaid"})
        config = merge_file_level(
            global_config,
            {"myst": {"fence_as_directive": "not-a-sequence"}},
            lambda kind, msg: warnings.append(msg),
        )
        assert len(warnings) == 1
        assert config.fence_as_directive == {"mermaid"}

    def test_an_unknown_field_is_reported(self):
        config, warnings = merge({"myst": {"not_a_field": 1}})
        assert warnings == ["Unknown field: not_a_field"]
        assert not hasattr(config, "not_a_field")


class TestUnaffectedBehaviour:
    """Guards for the paths the reordering runs through."""

    def test_a_plain_field_is_applied(self):
        config, warnings = merge({"myst": {"enable_extensions": ["dollarmath"]}})
        assert warnings == []
        assert "dollarmath" in config.enable_extensions

    def test_merge_topmatter_still_merges(self):
        """`substitutions` merges with the global value rather than replacing."""
        warnings: list[str] = []
        global_config = MdParserConfig(substitutions={"a": "global"})
        config = merge_file_level(
            global_config,
            {"myst": {"substitutions": {"b": "file"}}},
            lambda kind, msg: warnings.append(msg),
        )
        assert warnings == []
        assert config.substitutions == {"a": "global", "b": "file"}

    def test_the_file_level_value_wins_on_a_merged_field(self):
        warnings: list[str] = []
        global_config = MdParserConfig(substitutions={"a": "global"})
        config = merge_file_level(
            global_config,
            {"myst": {"substitutions": {"a": "file"}}},
            lambda kind, msg: warnings.append(msg),
        )
        assert config.substitutions == {"a": "file"}

    def test_the_global_config_is_not_mutated(self):
        global_config = MdParserConfig()
        merge_file_level(
            global_config,
            {"myst": {"enable_extensions": ["dollarmath"]}},
            lambda k, m: None,
        )
        assert "dollarmath" not in global_config.enable_extensions

    def test_a_non_dict_myst_key_is_reported(self):
        _config, warnings = merge({"myst": ["not", "a", "dict"]})
        assert len(warnings) == 1
        assert "not a dict" in warnings[0]


class TestMergedFieldsRejectNonMappings:
    """A ``merge_topmatter`` field given a non-mapping must warn, not raise.

    Merging ``{**global, **value}`` before validating ``value`` raised
    ``TypeError`` out of ``merge_file_level``, which aborted the whole build
    (docutils or Sphinx) where a warning is expected.
    """

    @pytest.mark.parametrize("name", ["substitutions", "html_meta"])
    @pytest.mark.parametrize("value", [["a", "b"], "just-a-string", 3, None], ids=repr)
    def test_a_non_mapping_is_reported_and_the_global_kept(self, name, value):
        warnings: list[tuple[MystWarnings, str]] = []
        global_config = MdParserConfig(**{name: {"a": "global"}})
        config = merge_file_level(
            global_config,
            {"myst": {name: value}},
            lambda kind, msg: warnings.append((kind, msg)),
        )
        assert len(warnings) == 1
        kind, msg = warnings[0]
        assert kind is MystWarnings.MD_TOPMATTER
        assert f"'{name}' must be of type" in msg
        assert getattr(config, name) == {"a": "global"}

    def test_a_non_mapping_does_not_abort_a_docutils_build(self):
        """End to end: the document is still built, with one topmatter warning."""
        stream = io.StringIO()
        doctree = publish_doctree(
            source="---\nmyst:\n  substitutions: [a, b]\n---\n\ntext\n",
            parser=Parser(),
            settings_overrides={"warning_stream": stream},
        )
        assert "'substitutions' must be of type" in stream.getvalue()
        assert "[myst.topmatter]" in stream.getvalue()
        assert "text" in doctree.astext()


class TestUrlSchemes:
    """``check_url_schemes`` converts both of its accepted forms to a dict.

    The converted form has to survive the merge: the raw list form, left on
    the config, crashed the build with ``list indices must be integers``.
    """

    def test_the_list_form_becomes_a_dict(self):
        config, warnings = merge({"myst": {"url_schemes": ["wiki"]}})
        assert warnings == []
        assert config.url_schemes == {"wiki": None}

    def test_the_dict_form_keeps_its_templates(self):
        config, warnings = merge(
            {"myst": {"url_schemes": {"wiki": "https://w.org/{{path}}"}}}
        )
        assert warnings == []
        assert config.url_schemes == {"wiki": {"url": "https://w.org/{{path}}"}}


class TestGlobalOnlyWarningKind:
    """The global-only rejection is a ``myst.topmatter`` warning.

    So it is reported under that code, and can be suppressed by it.
    """

    def test_the_warning_is_a_topmatter_warning(self):
        warnings: list[tuple[MystWarnings, str]] = []
        merge_file_level(
            MdParserConfig(),
            {"myst": {"heading_slug_func": "github"}},
            lambda kind, msg: warnings.append((kind, msg)),
        )
        assert [kind for kind, _msg in warnings] == [MystWarnings.MD_TOPMATTER]
