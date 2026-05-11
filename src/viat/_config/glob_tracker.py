import pathlib
from collections.abc import Sequence
from typing import cast

from viat.exceptions import ViatConfigError
from viat.protocols import ViatFileTracker
from viat.providers.tracker import GlobFileTracker, GlobFileTrackerConfig
from viat.support.json import Json, JsonArray, JsonObject
from viat.support.path_resolver import ViatPathResolver


def load_glob_tracker_from_config(resolver: ViatPathResolver, config: Json) -> ViatFileTracker:
    match config:
        case JsonObject() | None:
            tracker_config = GlobFileTrackerConfig(
                root=load_glob_tracker_root_from_config(resolver, config.get('root') if config else None),
                patterns=load_glob_tracker_patterns_from_config(config.get('patterns') if config else None),
                flags=load_glob_tracker_flags_from_config(config.get('flags') if config else None),
            )

            return GlobFileTracker(tracker_config)

        case _:
            raise ViatConfigError('The tracker.glob configuration must be a table')


def load_glob_tracker_root_from_config(resolver: ViatPathResolver, config: Json) -> pathlib.Path:
    match config:
        case str():
            return resolver.get_root() / config

        case None:
            return resolver.get_root()

        case _:
            raise ViatConfigError('The tracker.glob.root option must be a path')


def load_glob_tracker_patterns_from_config(config: Json) -> Sequence[str]:
    match config:
        case JsonArray():
            for pattern in config:
                if not isinstance(pattern, str):
                    raise ViatConfigError(f'Invalid glob pattern {pattern} in tracker.glob.patterns')

            return cast('Sequence[str]', config)

        case None:
            return []

        case _:
            raise ViatConfigError('The tracker.glob.patterns option must be an array of glob patterns')


def load_glob_tracker_flags_from_config(config: Json) -> str:
    match config:
        case str():
            # The tracker config initializer will validate the flags
            return config

        case None:
            return GlobFileTrackerConfig.flags

        case _:
            raise ViatConfigError('The tracker.glob.flags option must be a string of glob flags')
