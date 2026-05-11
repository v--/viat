import json
from types import TracebackType
from typing import override

import fastjsonschema

from viat.exceptions import ViatAttributeStorageError, ViatMalformedStoredDataError
from viat.protocols import ViatAttributeStorage
from viat.support.json import MutableJsonObject

from .config import JsonAttributeStorageConfig
from .connection import JsonAttributeStorageConnection


class JsonAttributeStorage(ViatAttributeStorage):
    """The JSON file storage class."""

    config: JsonAttributeStorageConfig
    _active_conn: JsonAttributeStorageConnection | None

    def __init__(self, config: JsonAttributeStorageConfig) -> None:
        self.config = config
        self._active_conn = None

    @override
    def __enter__(self) -> JsonAttributeStorageConnection:
        if self._active_conn:
            raise ViatAttributeStorageError('This storage already has an active connection')

        try:
            with open(self.config.storage_path) as file:
                json_doc = json.load(file)
        except FileNotFoundError:
            json_doc = {}
        except OSError as err:
            raise ViatAttributeStorageError('Could not read the storage file') from err
        except json.JSONDecodeError as err:
            raise ViatMalformedStoredDataError(self.config.storage_path) from err

        if not isinstance(json_doc, MutableJsonObject):
            raise ViatMalformedStoredDataError(self.config.storage_path)

        if self.config.json_schema_path:
            try:
                with open(self.config.json_schema_path) as file:
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

        self._active_conn = JsonAttributeStorageConnection(json_doc, validator)
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

        try:
            json_string = json.dumps(self._active_conn.payload, indent=self.config.indent)
        except json.JSONDecodeError as err:
            raise ViatAttributeStorageError('Could not serialize the stored attribute contents') from err
        finally:
            self._active_conn = None

        self.config.storage_path.write_text(json_string, encoding='utf-8')

