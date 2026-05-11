import pathlib

from viat.exceptions import ViatConfigError
from viat.protocols import ViatFileTracker
from viat.providers.tracker import GitFileTracker, GitFileTrackerConfig
from viat.support.json import Json, JsonObject
from viat.support.path_resolver import ViatPathResolver


def load_git_tracker_from_config(resolver: ViatPathResolver, config: Json) -> ViatFileTracker:
    match config:
        case JsonObject() | None:
            tracker_config = GitFileTrackerConfig(
                repo_root=load_git_tracker_repo_root_from_config(resolver, config.get('repo') if config else None),
                revision=load_git_tracker_revision_from_config(config.get('revision') if config else None),
                track_nonempty_directories=load_git_tracker_track_nonempty_directories_from_config(
                    config.get('track_nonempty_directories') if config else None,
                ),
            )

            return GitFileTracker(tracker_config)

        case _:
            raise ViatConfigError('The tracker.git configuration must be a table')


def load_git_tracker_repo_root_from_config(resolver: ViatPathResolver, config: Json) -> pathlib.Path:
    match config:
        case str():
            return resolver.get_root() / config

        case None:
            return resolver.get_root()

        case _:
            raise ViatConfigError('The tracker.git.repo option must be a path to a git repository')


def load_git_tracker_revision_from_config(config: Json) -> str:
    match config:
        case str():
            return config

        case None:
            return GitFileTrackerConfig.revision

        case _:
            raise ViatConfigError('The tracker.git.revision option must be a string specifying a git revision')


def load_git_tracker_track_nonempty_directories_from_config(config: Json) -> bool:
    match config:
        case bool():
            return config

        case None:
            return GitFileTrackerConfig.track_nonempty_directories

        case _:
            raise ViatConfigError('The tracker.git.track_nonempty_directories option must be a boolean')
