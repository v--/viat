import pathlib

from viat.exceptions import ViatConfigError
from viat.providers.storage import TomlAttributeStorage, TomlAttributeStorageConfig
from viat.support.json import Json, JsonObject
from viat.support.path_resolver import ViatPathResolver


def load_toml_storage_from_config(resolver: ViatPathResolver, config: Json) -> TomlAttributeStorage:
    match config:
        case JsonObject() | None:
            storage_config = TomlAttributeStorageConfig(
                storage_path=load_toml_storage_path_from_config(resolver, config.get('storage_path') if config else None),
                json_schema_path=load_toml_storage_schema_path_from_config(
                    resolver,
                    config.get('json_schema_path') if config else None,
                ),
            )

            return TomlAttributeStorage(storage_config)

        case _:
            raise ViatConfigError('The storage.toml configuration must be a table')


def load_toml_storage_path_from_config(resolver: ViatPathResolver, config: Json) -> pathlib.Path:
    match config:
        case str():
            return resolver.get_viat() / config

        case None:
            return resolver.get_viat() / 'storage.toml'

        case _:
            raise ViatConfigError('The storage.toml.storage_path option must be a path')


def load_toml_storage_schema_path_from_config(resolver: ViatPathResolver, config: Json) -> pathlib.Path | None:
    match config:
        case str():
            return resolver.get_viat() / config

        case None:
            default_path = resolver.get_viat() / 'schema.json'

            if default_path.exists():
                return default_path

            return None

        case _:
            raise ViatConfigError('The storage.toml.json_schema_path option must be a path')
