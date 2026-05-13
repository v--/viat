import contextlib
import pathlib
from collections.abc import Callable, Generator, Iterable, MutableMapping, MutableSet
from dataclasses import dataclass
from typing import override

import fastjsonschema

from viat._vault.resolver import ViatPathResolver
from viat.exceptions import (
    ViatAttributeStorageError,
    ViatMalformedStoredDataError,
    ViatStoredDataValidationWarning,
    ViatValidationError,
    emit_warning,
)
from viat.protocols import ViatAttributeStorageConnection
from viat.support.json import JsonObject, JsonObjectT, JsonT

from .mutator import JsonAttributeMutator
from .reader import JsonAttributeReader


@dataclass
class JsonAttributeStorageConnection(ViatAttributeStorageConnection):
    """A connection class for the JSON and TOML storages.

    Args:
        payload: The initial state of the storage.
        resolver: A path resolver used when creating readers and mutators.
        validator: A validator to be used on the contents of the storage.
    """

    payload: MutableMapping[str, JsonT]
    """The payload used to initialize the connection."""

    validator: Callable[[JsonT], None] | None
    """The validator used to initialize the connection."""

    resolver: ViatPathResolver | None
    """The resolver used to initialize the connection."""

    has_mutations: bool
    """An indicator whether the connection payload has been mutated."""

    _locked: MutableSet[pathlib.Path]

    def __init__(
        self,
        payload: MutableMapping[str, JsonT],
        resolver: ViatPathResolver | None = None,
        validator: Callable[[JsonT], None] | None = None,
    ) -> None:
        self.payload = payload
        self.resolver =resolver
        self.validator = validator
        self.has_mutations = False
        self._locked = set[pathlib.Path]()

        if validator:
            for key, value in self.payload.items():
                if not isinstance(value, JsonObject):
                    raise ViatMalformedStoredDataError(pathlib.Path(key))

                if self.validator:
                    try:
                        self.validator(value)
                    except fastjsonschema.JsonSchemaValueException as err:
                        emit_warning(
                            ViatStoredDataValidationWarning(pathlib.Path(key), err),
                            stacklevel=2,
                        )

    def _resolve_path(self, path: pathlib.Path | str) -> pathlib.Path:
        return self.resolver.relativize(path) if self.resolver else pathlib.Path(path)

    @contextlib.contextmanager
    def get_reader(self, path: pathlib.Path | str) -> Generator[JsonAttributeReader]:
        rel_path = self._resolve_path(path)

        if rel_path in self._locked:
            raise ViatAttributeStorageError(f'There is already an active reader or mutator for {rel_path.as_posix()!r}')

        stored_data = self.payload.get(rel_path.as_posix())

        if stored_data is not None and not isinstance(stored_data, JsonObject):
            raise ViatMalformedStoredDataError(rel_path)

        payload: JsonObjectT = stored_data or {}
        self._locked.add(rel_path)

        try:
            yield JsonAttributeReader(rel_path, payload)
        finally:
            self._locked.remove(rel_path)

    @contextlib.contextmanager
    def get_mutator(self, path: pathlib.Path | str) -> Generator[JsonAttributeMutator]:
        rel_path = self._resolve_path(path)

        if rel_path in self._locked:
            raise ViatAttributeStorageError(f'There is already an active reader or mutator for {rel_path.as_posix()!r}')

        stored_data = self.payload.get(rel_path.as_posix())

        if stored_data is not None and not isinstance(stored_data, MutableMapping):
            raise ViatMalformedStoredDataError(rel_path)

        payload: MutableMapping[str, JsonT] = stored_data or {}
        self._locked.add(rel_path)
        self.has_mutations = True

        try:
            yield JsonAttributeMutator(rel_path, payload)
        finally:
            self._locked.remove(rel_path)

        if len(payload) == 0:
            if stored_data is not None:
                del self.payload[rel_path.as_posix()]

            return

        if self.validator:
            try:
                self.validator(payload)
            except fastjsonschema.JsonSchemaValueException as err:
                raise ViatValidationError(rel_path) from err

        self.payload[rel_path.as_posix()] = payload

    @override
    def iter_known_paths(self) -> Iterable[pathlib.Path]:
        for key in self.payload:
            yield pathlib.Path(key)
