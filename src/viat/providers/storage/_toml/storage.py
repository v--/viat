import pathlib
import tomllib
from collections.abc import MutableMapping
from typing import override

import tomli_w

from viat import ViatAttributeStorage
from viat._vault.resolver import ViatPathResolver
from viat.exceptions import ViatAttributeStorageError, ViatMalformedStoredDataError
from viat.providers.storage._json.storage_mixin import JsonAttributeStorageMixin
from viat.support.json import JsonObjectT, JsonT

from .config import TomlAttributeStorageConfig


class TomlAttributeStorage(JsonAttributeStorageMixin, ViatAttributeStorage):
    """The TOML file storage class.

    Args:
        config: All configuration required for the storage.
        resolver: A path resolver used by connections.
    """

    config: TomlAttributeStorageConfig
    """The configuration used to initialize the storage."""

    resolver: ViatPathResolver | None
    """The resolver used to initialize the storage."""

    def __init__(
        self,
        config: TomlAttributeStorageConfig,
        resolver: ViatPathResolver | None = None,
    ) -> None:
        self.config = config
        self.resolver = resolver

    @override
    def _get_json_schema_path(self) -> pathlib.Path | None:
        return self.config.json_schema_path

    @override
    def _load_storage_data(self) -> MutableMapping[str, JsonT]:
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
    def _dump_storage_data(self, data: JsonObjectT) -> None:
        try:
            toml_string = tomli_w.dumps(data)
        except (ValueError, TypeError) as err:
            raise ViatAttributeStorageError('Could not serialize the stored attribute contents') from err
        finally:
            self._active_conn = None

        self.config.storage_path.write_text(toml_string, encoding='utf-8')
