import pathlib
from collections.abc import Iterator, Mapping

import tomlkit
import tomlkit.container
import tomlkit.exceptions
import tomlkit.items

from viat.exceptions import ViatMissingAttributeError
from viat.protocols import ViatAttributeReader
from viat.support.json import Json
from viat.support.toml import toml_to_json


class TomlAttributeReader(Mapping[str, Json], ViatAttributeReader):
    """A storage reader for TOMLKit tables.

    Args:
        path: The path to which the table corresponds.
        toml_table: The TOMLKit table.
    """

    path: pathlib.Path
    """The path used to initialize the reader."""

    toml_table: tomlkit.items.Table
    """The table used to initialize the reader."""

    def __init__(self, path: pathlib.Path, toml_table: tomlkit.items.Table) -> None:
        self.path = path
        self.toml_table = toml_table

    def __getitem__(self, key: str) -> Json:
        try:
            value = self.toml_table[key]
        except KeyError:
            raise ViatMissingAttributeError(self.path, key) from None

        return toml_to_json(value)

    def __iter__(self) -> Iterator[str]:
        return iter(self.toml_table)

    def __len__(self) -> int:
        return len(self.toml_table)
