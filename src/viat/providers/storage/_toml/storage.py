import json
from types import TracebackType
from typing import override

import fastjsonschema
import tomlkit
import tomlkit.exceptions

from viat.exceptions import ViatAttributeStorageError, ViatMalformedStoredDataError
from viat.protocols import ViatAttributeStorage

from .config import TomlAttributeStorageConfig
from .connection import TomlAttributeStorageConnection


class TomlAttributeStorage(ViatAttributeStorage):
    """The TOML file storage class."""

    config: TomlAttributeStorageConfig
    _active_conn: TomlAttributeStorageConnection | None

    def __init__(self, config: TomlAttributeStorageConfig) -> None:
        self.config = config
        self._active_conn = None

    @override
    def __enter__(self) -> TomlAttributeStorageConnection:
        if self._active_conn:
            raise ViatAttributeStorageError('This storage already has an active connection')

        try:
            with open(self.config.storage_path) as file:
                toml_doc = tomlkit.load(file)
        except FileNotFoundError:
            toml_doc = tomlkit.TOMLDocument()
        except OSError as err:
            raise ViatAttributeStorageError('Could not read the storage file') from err
        except tomlkit.exceptions.TOMLKitError as err:
            raise ViatMalformedStoredDataError(self.config.storage_path) from err

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

        self._active_conn = TomlAttributeStorageConnection(toml_doc, validator)
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

        if not self._active_conn.has_mutations:
            self._active_conn = None
            return

        try:
            toml_string = tomlkit.dumps(self._active_conn.payload)
        except json.JSONDecodeError as err:
            raise ViatAttributeStorageError('Could not serialize the stored attribute contents') from err
        finally:
            self._active_conn = None

        self.config.storage_path.write_text(toml_string, encoding='utf-8')
