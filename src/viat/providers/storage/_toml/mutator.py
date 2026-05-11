import pathlib
from collections.abc import MutableMapping

import tomlkit
import tomlkit.container
import tomlkit.exceptions
import tomlkit.items

from viat.exceptions import MissingAttributeError
from viat.protocols import ViatAttributeMutator
from viat.support.json import Json

from .reader import TomlAttributeReader


class TomlAttributeMutator(MutableMapping[str, Json], TomlAttributeReader, ViatAttributeMutator):
    """A storage mutator for TOMLKit tables.

    Args:
        path: The path to which the table corresponds.
        toml_table: The TOMLKit table.
    """

    path: pathlib.Path
    """The path used to initialize the mutator."""

    toml_table: tomlkit.items.Table
    """The table used to initialize the mutator."""

    def __setitem__(self, key: str, value: Json) -> None:
        self.toml_table[key] = value

    def __delitem__(self, key: str) -> None:
        try:
            del self.toml_table[key]
        except KeyError:
            raise MissingAttributeError(self.path, key) from None
