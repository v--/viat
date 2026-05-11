import contextlib
import pathlib
from collections.abc import Callable, Generator, Iterable, MutableSet
from dataclasses import dataclass
from typing import override

import fastjsonschema
import tomlkit
import tomlkit.container
import tomlkit.exceptions
import tomlkit.items

from viat.exceptions import (
    ViatAttributeStorageError,
    ViatMalformedStoredDataError,
    ViatStoredDataValidationWarning,
    ViatValidationError,
    process_warning,
)
from viat.protocols import ViatAttributeStorageConnection
from viat.support.json import Json
from viat.support.toml import toml_to_json

from .mutator import TomlAttributeMutator
from .reader import TomlAttributeReader


@dataclass
class TomlAttributeStorageConnection(ViatAttributeStorageConnection):
    """A connection class for the TOML storage.

    Args:
        payload: The initial state of the storage.
        validator: A validator to be used on the contents of the storage.
    """

    payload: tomlkit.TOMLDocument
    validator: Callable[[Json], None] | None
    has_mutations: bool
    _active_managers: MutableSet[pathlib.Path]

    def __init__(self, payload: tomlkit.TOMLDocument, validator: Callable[[Json], None] | None) -> None:
        self.payload = payload
        self.validator = validator
        self.has_mutations = False
        self._locked = set[pathlib.Path]()

        if validator:
            for key, value in self.payload.items():
                if not isinstance(value, tomlkit.items.Table):
                    raise ViatMalformedStoredDataError(pathlib.Path(key))

                if self.validator:
                    try:
                        self.validator(toml_to_json(value))
                    except fastjsonschema.JsonSchemaValueException as err:
                        process_warning(
                            ViatStoredDataValidationWarning(pathlib.Path(key), err),
                            stacklevel=2,
                        )

    @contextlib.contextmanager
    def get_reader(self, path: pathlib.Path | str) -> Generator[TomlAttributeReader]:
        npath = pathlib.Path(path)

        if npath in self._locked:
            raise ViatAttributeStorageError(f'There is already an active reader or mutator for {npath.as_posix()!r}')

        stored_table = self.payload.get(npath.as_posix())

        if stored_table is not None and not isinstance(stored_table, tomlkit.items.Table):
            raise ViatMalformedStoredDataError(npath)

        payload = stored_table or tomlkit.table()
        self._locked.add(npath)

        try:
            yield TomlAttributeReader(npath, payload)
        finally:
            self._locked.remove(npath)

    @contextlib.contextmanager
    def get_mutator(self, path: pathlib.Path | str) -> Generator[TomlAttributeMutator]:
        npath = pathlib.Path(path)

        if npath in self._locked:
            raise ViatAttributeStorageError(f'There is already an active reader or mutator for {npath.as_posix()!r}')

        stored_table = self.payload.get(npath.as_posix())

        if stored_table is not None and not isinstance(stored_table, tomlkit.items.Table):
            raise ViatMalformedStoredDataError(npath)

        payload = stored_table or tomlkit.table()
        self._locked.add(npath)
        self.has_mutations = True

        try:
            yield TomlAttributeMutator(npath, payload)
        finally:
            self._locked.remove(npath)

        if len(payload) == 0:
            if stored_table is not None:
                del self.payload[npath.as_posix()]

            return

        if self.validator:
            try:
                self.validator(toml_to_json(payload))
            except fastjsonschema.JsonSchemaValueException as err:
                raise ViatValidationError(npath) from err

        self.payload[npath.as_posix()] = payload

    @override
    def iter_known_paths(self) -> Iterable[pathlib.Path]:
        for key in self.payload:
            yield pathlib.Path(key)
