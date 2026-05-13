import json
import pathlib
from collections.abc import MutableMapping
from types import TracebackType
from typing import override

import fastjsonschema

from viat._vault.resolver import ViatPathResolver
from viat.exceptions import ViatAttributeStorageError
from viat.protocols import ViatAttributeStorage
from viat.providers.storage._json.connection import JsonAttributeStorageConnection
from viat.support.json import JsonObjectT, JsonT


class JsonAttributeStorageMixin(ViatAttributeStorage):
    _active_conn: JsonAttributeStorageConnection | None = None
    resolver: ViatPathResolver | None

    def _get_json_schema_path(self) -> pathlib.Path | None:
        raise NotImplementedError

    def _load_storage_data(self) -> MutableMapping[str, JsonT]:
        raise NotImplementedError

    def _dump_storage_data(self, data: JsonObjectT) -> None:
        raise NotImplementedError

    @override
    def __enter__(self) -> JsonAttributeStorageConnection:
        if self._active_conn:
            raise ViatAttributeStorageError('This storage already has an active connection')

        storage_payload = self._load_storage_data()

        if json_schema_path := self._get_json_schema_path():
            try:
                with json_schema_path.open() as file:
                    schema_content = json.load(file)
                    validator = fastjsonschema.compile(schema_content)
            except OSError as err:
                raise ViatAttributeStorageError('Could not read the schema file') from err
            except json.JSONDecodeError as err:
                raise ViatAttributeStorageError('Could not decode the schema file') from err
            except fastjsonschema.JsonSchemaDefinitionException as err:
                raise ViatAttributeStorageError('Invalid schema file') from err
        else:
            validator = None

        self._active_conn = JsonAttributeStorageConnection(storage_payload, self.resolver, validator)
        return self._active_conn

    @override
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
     ) -> None:
        if not self._active_conn:
            raise ViatAttributeStorageError('This storage has no active connection')

        if exc_value or not self._active_conn.has_mutations:
            self._active_conn = None
            return

        self._dump_storage_data(self._active_conn.payload)
