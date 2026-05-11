import contextlib
import pathlib
from collections.abc import Callable, Generator, Iterable, MutableSet
from dataclasses import dataclass
from typing import override

import fastjsonschema

from viat.exceptions import (
    ViatAttributeStorageError,
    ViatMalformedStoredDataError,
    ViatStoredDataValidationWarning,
    ViatValidationError,
    process_warning,
)
from viat.protocols import ViatAttributeStorageConnection
from viat.support.json import Json, MutableJsonObject
from viat.support.stdlib_protocols import MutableMappingProtocol

from .mutator import JsonAttributeMutator
from .reader import JsonAttributeReader


@dataclass
class JsonAttributeStorageConnection(ViatAttributeStorageConnection):
    """A connection class for the TOML storage.

    Args:
        payload: The initial state of the storage.
        validator: A validator to be used on the contents of the storage.
    """

    payload: MutableJsonObject
    validator: Callable[[Json], None] | None
    _locked: MutableSet[pathlib.Path]

    def __init__(self, payload: MutableMappingProtocol[str, Json], validator: Callable[[Json], None] | None) -> None:
        self.payload = payload
        self.validator = validator
        self._locked = set[pathlib.Path]()

        if validator:
            for key, value in self.payload.items():
                if not isinstance(value, MutableJsonObject):
                    raise ViatMalformedStoredDataError(pathlib.Path(key))

                if self.validator:
                    try:
                        self.validator(value)
                    except fastjsonschema.JsonSchemaValueException as err:
                        process_warning(
                            ViatStoredDataValidationWarning(pathlib.Path(key), err),
                            stacklevel=2,
                        )

    @contextlib.contextmanager
    def get_reader(self, path: pathlib.Path) -> Generator[JsonAttributeReader]:
        if path in self._locked:
            raise ViatAttributeStorageError(f'There is already an active reader or mutator for {path.as_posix()!r}')

        stored_data = self.payload.get(path.as_posix())

        if stored_data is not None and not isinstance(stored_data, MutableJsonObject):
            raise ViatMalformedStoredDataError(path)

        payload = stored_data or {}
        self._locked.add(path)

        try:
            yield JsonAttributeReader(path, payload)
        finally:
            self._locked.remove(path)

    @contextlib.contextmanager
    def get_mutator(self, path: pathlib.Path) -> Generator[JsonAttributeMutator]:
        if path in self._locked:
            raise ViatAttributeStorageError(f'There is already an active reader or mutator for {path.as_posix()!r}')

        stored_data = self.payload.get(path.as_posix())

        if stored_data is not None and not isinstance(stored_data, MutableJsonObject):
            raise ViatMalformedStoredDataError(path)

        payload = stored_data or {}
        self._locked.add(path)

        try:
            yield JsonAttributeMutator(path, payload)
        finally:
            self._locked.remove(path)

        if len(payload) == 0:
            if stored_data is not None:
                del self.payload[path.as_posix()]

            return

        if self.validator:
            try:
                self.validator(payload)
            except fastjsonschema.JsonSchemaValueException as err:
                raise ViatValidationError(path) from err

        self.payload[path.as_posix()] = payload

    @override
    def iter_known_paths(self) -> Iterable[pathlib.Path]:
        for key in self.payload:
            yield pathlib.Path(key)
