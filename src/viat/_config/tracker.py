from viat.exceptions import ViatConfigError
from viat.protocols import ViatFileTracker
from viat.support.json import Json, JsonObject
from viat.support.path_resolver import ViatPathResolver

from .git_tracker import load_git_tracker_from_config
from .glob_tracker import load_glob_tracker_from_config


def load_tracker_from_config(resolver: ViatPathResolver, config: Json) -> ViatFileTracker:
    match config:
        case JsonObject():
            match config.get('provider'):
                case 'glob' | None:
                    return load_glob_tracker_from_config(resolver, config.get('glob'))

                case 'git':
                    return load_git_tracker_from_config(resolver, config.get('git'))

                case _:
                    raise ViatConfigError('The tracker.provider setting must be either "glob" or "git"')

        case None:
            return load_glob_tracker_from_config(resolver, None)

        case _:
            raise ViatConfigError('The tracker configuration must be a table')
