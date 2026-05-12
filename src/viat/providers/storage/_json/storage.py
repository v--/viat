import json
import pathlib
from types import TracebackType
from typing import override

import fastjsonschema

from viat.exceptions import ViatAttributeStorageError, ViatMalformedStoredDataError
from viat.protocols import ViatAttributeStorage
from viat.support.json import JsonObject, MutableJsonObject

from .config import JsonAttributeStorageConfig
from .connection import JsonAttributeStorageConnection


class AbstractJsonAttributeStorage(ViatAttributeStorage):
    """An abstract implementation of JSON-based attribute storage. Used for JSON and TOML."""

    _active_conn: JsonAttributeStorageConnection | None = None

    def get_json_schema_path(self) -> pathlib.Path | None:
        """Get the path to an optional JSON schema file."""
        raise NotImplementedError

    def load_storage_data(self) -> MutableJsonObject:
        """Load the stored data as a mutable JSON object."""
        raise NotImplementedError

    def dump_storage_data(self, data: JsonObject) -> None:
        """Dump a JSON object to the storage backend."""
        raise NotImplementedError

    @override
    def __enter__(self) -> JsonAttributeStorageConnection:
        if self._active_conn:
            raise ViatAttributeStorageError('This storage already has an active connection')

        storage_payload = self.load_storage_data()

        if json_schema_path := self.get_json_schema_path():
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

        self._active_conn = JsonAttributeStorageConnection(storage_payload, validator)
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

        self.dump_storage_data(self._active_conn.payload)


class JsonAttributeStorage(AbstractJsonAttributeStorage):
    """The JSON file storage class."""

    config: JsonAttributeStorageConfig

    def __init__(self, config: JsonAttributeStorageConfig) -> None:
        self.config = config

    @override
    def get_json_schema_path(self) -> pathlib.Path | None:
        return self.config.json_schema_path

    @override
    def load_storage_data(self) -> MutableJsonObject:
        try:
            with self.config.storage_path.open() as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
        except OSError as err:
            raise ViatAttributeStorageError('Could not read the storage file') from err
        except json.JSONDecodeError as err:
            raise ViatMalformedStoredDataError(self.config.storage_path) from err

    @override
    def dump_storage_data(self, data: JsonObject) -> None:
        try:
            json_string = json.dumps(data, indent=self.config.indent)
        except json.JSONDecodeError as err:
            raise ViatAttributeStorageError('Could not serialize the stored attribute contents') from err
        finally:
            self._active_conn = None

        self.config.storage_path.write_text(json_string, encoding='utf-8')
