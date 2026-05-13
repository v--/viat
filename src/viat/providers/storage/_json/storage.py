import json
import pathlib
from typing import override

from viat._vault.resolver import ViatPathResolver
from viat.exceptions import ViatAttributeStorageError, ViatMalformedStoredDataError
from viat.protocols import ViatAttributeStorage
from viat.support.json import JsonObject, MutableJsonObject

from .config import JsonAttributeStorageConfig
from .storage_mixin import JsonAttributeStorageMixin


class JsonAttributeStorage(JsonAttributeStorageMixin, ViatAttributeStorage):
    """The JSON file storage class.

    Args:
        config: All configuration required for the storage.
        resolver: A path resolver used by connections.
    """

    config: JsonAttributeStorageConfig
    """The configuration used to initialize the storage."""

    resolver: ViatPathResolver | None
    """The resolver used to initialize the storage."""

    def __init__(
        self,
        config: JsonAttributeStorageConfig,
        resolver: ViatPathResolver | None = None,
    ) -> None:
        self.config = config
        self.resolver = resolver

    @override
    def _get_json_schema_path(self) -> pathlib.Path | None:
        return self.config.json_schema_path

    @override
    def _load_storage_data(self) -> MutableJsonObject:
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
    def _dump_storage_data(self, data: JsonObject) -> None:
        try:
            json_string = json.dumps(data, indent=self.config.indent)
        except json.JSONDecodeError as err:
            raise ViatAttributeStorageError('Could not serialize the stored attribute contents') from err
        finally:
            self._active_conn = None

        self.config.storage_path.write_text(json_string, encoding='utf-8')
