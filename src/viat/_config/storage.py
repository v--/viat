from viat._config.loader import ConfigLoader
from viat._vault_config import ViatVaultStaticConfig
from viat.exceptions import ViatConfigError
from viat.protocols import ViatAttributeStorage
from viat.providers.storage import (
    JsonAttributeStorage,
    JsonAttributeStorageConfig,
    TomlAttributeStorage,
    TomlAttributeStorageConfig,
)
from viat.support.path_resolver import ViatPathResolver


def load_storage_from_config(resolver: ViatPathResolver, static_config: ViatVaultStaticConfig, loader: ConfigLoader) -> ViatAttributeStorage:
    match loader.get_str('storage', 'provider'):
        case 'toml' | None:
            return load_toml_storage_from_config(resolver, static_config, loader)

        case 'json':
            return load_json_storage_from_config(resolver, static_config, loader)

        case _:
            raise ViatConfigError('The storage.provider option must be either "toml" or "json"')


def load_toml_storage_from_config(resolver: ViatPathResolver, static_config: ViatVaultStaticConfig, loader: ConfigLoader) -> TomlAttributeStorage:
    storage_path = loader.get_path('storage', 'toml', 'storage_path', root=resolver.get_viat(), default=resolver.get_viat() / 'storage.toml')

    if static_config.skip_validation:
        schema_path = None
    else:
        schema_path = loader.get_path('storage', 'toml', 'json_schema_path', root=resolver.get_viat())

        if schema_path is None and resolver.get_viat().joinpath('schema.json').exists():
            schema_path = resolver.get_viat() / 'schema.json'

    storage_config = TomlAttributeStorageConfig(storage_path, schema_path)
    return TomlAttributeStorage(storage_config)


def load_json_storage_from_config(resolver: ViatPathResolver, static_config: ViatVaultStaticConfig, loader: ConfigLoader) -> JsonAttributeStorage:
    storage_path = loader.get_path('storage', 'json', 'storage_path', root=resolver.get_viat(), default=resolver.get_viat() / 'storage.json')

    if static_config.skip_validation:
        schema_path = None
    else:
        schema_path = loader.get_path('storage', 'json', 'json_schema_path', root=resolver.get_viat())

        if schema_path is None and resolver.get_viat().joinpath('schema.json').exists():
            schema_path = resolver.get_viat() / 'schema.json'

    indent = loader.get_nested('storage', 'json', 'indent')

    if indent is not None and not isinstance(indent, (str, int)):
        raise ViatConfigError('The storage.json.indent option must be a string or int')

    storage_config = JsonAttributeStorageConfig(storage_path, schema_path, indent)
    return JsonAttributeStorage(storage_config)

