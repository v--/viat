from viat.exceptions import ViatConfigError
from viat.protocols import ViatAttributeStorage
from viat.support.json import Json, JsonObject
from viat.support.path_resolver import ViatPathResolver

from .json_storage import load_json_storage_from_config
from .toml_storage import load_toml_storage_from_config


def load_storage_from_config(resolver: ViatPathResolver, config: Json) -> ViatAttributeStorage:
    match config:
        case JsonObject():
            match config.get('provider'):
                case 'toml' | None:
                    return load_toml_storage_from_config(resolver, config.get('toml'))

                case 'json':
                    return load_json_storage_from_config(resolver, config.get('json'))

                case _:
                    raise ViatConfigError('The storage.provider setting must be either "toml" or "json"')

        case None:
            return load_toml_storage_from_config(resolver, None)

        case _:
            raise ViatConfigError('The storage configuration must be a table')
