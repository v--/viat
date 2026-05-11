"""Utilities for working with TOML."""

import tomlkit
import tomlkit.container
import tomlkit.exceptions
import tomlkit.items

from viat.exceptions import ViatIntegrityError
from viat.support.json import Json


def toml_to_json(value: object) -> Json:
    """Convert a TOMLKit value to JSON.

    Args:
        value: A value produced by TOMLKit.

    Returns:
        A JSON representation.
    """
    match value:
        case tomlkit.items.Item() | tomlkit.container.Container():
            return value.unwrap()

        case int() | float() | str():
            return value

        case _:
            raise ViatIntegrityError(f'Unrecognized TOML object type {value}')
