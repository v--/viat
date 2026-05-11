import pathlib

from viat.exceptions import ViatConfigError
from viat.providers.storage import JsonAttributeStorage, JsonAttributeStorageConfig
from viat.support.json import Json, JsonObject
from viat.support.path_resolver import ViatPathResolver


def load_json_storage_from_config(resolver: ViatPathResolver, config: Json) -> JsonAttributeStorage:
    match config:
        case JsonObject() | None:
            storage_config = JsonAttributeStorageConfig(
                storage_path=load_json_storage_path_from_config(resolver, config.get('storage_path') if config else None),
                indent=load_json_storage_indent_from_config(config.get('indent') if config else None),
                json_schema_path=load_json_storage_schema_path_from_config(
                    resolver,
                    config.get('json_schema_path') if config else None,
                ),
            )

            return JsonAttributeStorage(storage_config)

        case _:
            raise ViatConfigError('The storage.json configuration must be a table')


def load_json_storage_path_from_config(resolver: ViatPathResolver, config: Json) -> pathlib.Path:
    match config:
        case str():
            return resolver.get_viat() / config

        case None:
            return resolver.get_viat() / 'storage.json'

        case _:
            raise ViatConfigError('The storage.json.storage_path option must be a path')


def load_json_storage_indent_from_config(config: Json) -> str | int | None:
    match config:
        case str() | int() | None:
            return config

        case _:
            raise ViatConfigError('The storage.json.indent option must be a string or int')


def load_json_storage_schema_path_from_config(resolver: ViatPathResolver, config: Json) -> pathlib.Path | None:
    match config:
        case str():
            return resolver.get_viat() / config

        case None:
            default_path = resolver.get_viat() / 'schema.json'

            if default_path.exists():
                return default_path

            return None

        case _:
            raise ViatConfigError('The storage.json.json_schema_path option must be a path')
