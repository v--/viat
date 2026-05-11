from collections.abc import Sequence
from typing import cast

from viat._config.loader import ConfigLoader
from viat.exceptions import ViatConfigError
from viat.protocols import ViatFileTracker
from viat.providers.tracker import GitFileTracker, GitFileTrackerConfig, GlobFileTracker, GlobFileTrackerConfig
from viat.support.json import JsonArray
from viat.support.path_resolver import ViatPathResolver


def load_tracker_from_config(resolver: ViatPathResolver, loader: ConfigLoader) -> ViatFileTracker:
    match loader.get_str('tracker', 'provider'):
        case 'glob' | None:
            return load_glob_tracker_from_config(resolver, loader)

        case 'git':
            return load_git_tracker_from_config(resolver, loader)

        case _:
            raise ViatConfigError('The tracker.provider option must be either "glob" or "git"')


def load_glob_tracker_from_config(resolver: ViatPathResolver, loader: ConfigLoader) -> ViatFileTracker:
    tracker_config = GlobFileTrackerConfig(
        root=loader.get_path('tracker', 'glob', 'root', root=resolver.get_root(), default=resolver.get_root()),
        patterns=load_glob_tracker_patterns_from_config(loader),
        # The tracker config initializer will validate the flags
        flags=loader.get_str('tracker', 'glob', 'flags', default=GlobFileTrackerConfig.flags),
    )

    return GlobFileTracker(tracker_config)


def load_glob_tracker_patterns_from_config(loader: ConfigLoader) -> Sequence[str]:
    match patterns := loader.get_nested('tracker', 'glob', 'patterns'):
        case JsonArray():
            for pattern in patterns:
                if not isinstance(pattern, str):
                    raise ViatConfigError(f'Invalid glob pattern {pattern} in tracker.glob.patterns')

            return cast('Sequence[str]', patterns)

        case None:
            return []

        case _:
            raise ViatConfigError('The tracker.glob.patterns option must be an array of glob patterns')


def load_git_tracker_from_config(resolver: ViatPathResolver, loader: ConfigLoader) -> ViatFileTracker:
    tracker_config = GitFileTrackerConfig(
        repo_root=loader.get_path('tracker', 'git', 'repo_root', root=resolver.get_root(), default=resolver.get_root()),
        revision=loader.get_str('tracker', 'git', 'revision', default=GitFileTrackerConfig.revision),
        track_nonempty_directories=loader.get_bool(
            'tracker', 'git', 'track_nonempty_directories',
            default=GitFileTrackerConfig.track_nonempty_directories,
        ),
    )

    return GitFileTracker(tracker_config)

