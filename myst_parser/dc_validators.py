"""Validators for dataclasses, mirroring those of https://github.com/python-attrs/attrs."""
from __future__ import annotations

import dataclasses as dc
from typing import Any, Callable, Sequence, Type


def validate_fields(inst):
    """Validate the fields of a dataclass,
    according to `validator` functions set in the field metadata.

    This function should be called in the `__post_init__` of the dataclass.

    The validator function should take as input (inst, field, value) and
    raise an exception if the value is invalid.
    """
    for field in dc.fields(inst):
        if "validator" not in field.metadata:
            continue
        if isinstance(field.metadata["validator"], list):
            for validator in field.metadata["validator"]:
                validator(inst, field, getattr(inst, field.name))
        else:
            field.metadata["validator"](inst, field, getattr(inst, field.name))


ValidatorType = Callable[[Any, dc.Field, Any], None]


def instance_of(type: Type[Any] | tuple[Type[Any], ...]) -> ValidatorType:
    """
    A validator that raises a `TypeError` if the initializer is called
    with a wrong type for this particular attribute (checks are performed using
    `isinstance` therefore it's also valid to pass a tuple of types).

    :param type: The type to check for.
    """

    def _validator(inst, attr, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if not isinstance(value, type):
            raise TypeError(
                f"'{attr.name}' must be {type!r} (got {value!r} that is a {value.__class__!r})."
            )

    return _validator


def optional(validator: ValidatorType) -> ValidatorType:
    """
    A validator that makes an attribute optional.  An optional attribute is one
    which can be set to ``None`` in addition to satisfying the requirements of
    the sub-validator.
    """

    def _validator(inst, attr, value):
        if value is None:
            return

        validator(inst, attr, value)

    return _validator


def is_callable(inst, attr, value):
    """
    A validator that raises a `TypeError` if the
    initializer is called with a value for this particular attribute
    that is not callable.
    """
    if not callable(value):
        raise TypeError(
            f"'{attr.name}' must be callable "
            f"(got {value!r} that is a {value.__class__!r})."
        )


def in_(options: Sequence) -> ValidatorType:
    """
    A validator that raises a `ValueError` if the initializer is called
    with a value that does not belong in the options provided.  The check is
    performed using ``value in options``.

    :param options: Allowed options.
    """

    def _validator(inst, attr, value):
        try:
            in_options = value in options
        except TypeError:  # e.g. `1 in "abc"`
            in_options = False

        if not in_options:
            raise ValueError(f"'{attr.name}' must be in {options!r} (got {value!r})")

    return _validator


def deep_iterable(
    member_validator: ValidatorType, iterable_validator: ValidatorType | None = None
) -> ValidatorType:
    """
    A validator that performs deep validation of an iterable.

    :param member_validator: Validator to apply to iterable members
    :param iterable_validator: Validator to apply to iterable itself
    """

    def _validator(inst, attr, value):
        if iterable_validator is not None:
            iterable_validator(inst, attr, value)

        for member in value:
            member_validator(inst, attr, member)

    return _validator


def deep_mapping(
    key_validator: ValidatorType,
    value_validator: ValidatorType,
    mapping_validator: ValidatorType | None = None,
) -> ValidatorType:
    """
    A validator that performs deep validation of a dictionary.

    :param key_validator: Validator to apply to dictionary keys
    :param value_validator: Validator to apply to dictionary values
    :param mapping_validator: Validator to apply to top-level mapping attribute (optional)
    """

    def _validator(inst, attr, value):
        if mapping_validator is not None:
            mapping_validator(inst, attr, value)

        for key in value:
            key_validator(inst, attr, key)
            value_validator(inst, attr, value[key])

    return _validator
