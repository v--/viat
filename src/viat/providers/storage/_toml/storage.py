import pathlib
import tomllib
from typing import override

import tomli_w

from viat.exceptions import ViatAttributeStorageError, ViatMalformedStoredDataError
from viat.providers.storage.json import AbstractJsonAttributeStorage
from viat.support.json import JsonObject, MutableJsonObject

from .config import TomlAttributeStorageConfig


class TomlAttributeStorage(AbstractJsonAttributeStorage):
    """The TOML file storage class."""

    config: TomlAttributeStorageConfig

    def __init__(self, config: TomlAttributeStorageConfig) -> None:
        self.config = config

    @override
    def get_json_schema_path(self) -> pathlib.Path | None:
        return self.config.json_schema_path

    @override
    def load_storage_data(self) -> MutableJsonObject:
        try:
            with self.config.storage_path.open('rb') as file:
                return tomllib.load(file)
        except FileNotFoundError:
            return {}
        except OSError as err:
            raise ViatAttributeStorageError('Could not read the storage file') from err
        except tomllib.TOMLDecodeError as err:
            raise ViatMalformedStoredDataError(self.config.storage_path) from err

    @override
    def dump_storage_data(self, data: JsonObject) -> None:
        try:
            toml_string = tomli_w.dumps(data)
        except (ValueError, TypeError) as err:
            raise ViatAttributeStorageError('Could not serialize the stored attribute contents') from err
        finally:
            self._active_conn = None

        self.config.storage_path.write_text(toml_string, encoding='utf-8')
