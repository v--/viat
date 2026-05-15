from collections.abc import Sequence
from typing import cast

from viat._config.loader import ConfigLoader
from viat._vault.config import ViatVaultStaticConfig
from viat._vault.resolver import ViatPathResolver
from viat.exceptions import ViatConfigError
from viat.protocols import ViatFileTracker
from viat.providers.tracker import GitFileTracker, GitFileTrackerConfig, GlobFileTracker, GlobFileTrackerConfig
from viat.providers.tracker.glob import DEFAULT_GLOB_FLAGS
from viat.support.json import JsonArray


def load_tracker_from_config(resolver: ViatPathResolver, static_config: ViatVaultStaticConfig, loader: ConfigLoader) -> ViatFileTracker:
    match loader.get_str('tracker', 'provider'):
        case 'glob' | None:
            return load_glob_tracker_from_config(resolver, static_config, loader)

        case 'git':
            return load_git_tracker_from_config(resolver, static_config, loader)

        case _:
            raise ViatConfigError('The tracker.provider option must be either "glob" or "git"')


def load_glob_tracker_from_config(resolver: ViatPathResolver, static_config: ViatVaultStaticConfig, loader: ConfigLoader) -> ViatFileTracker:
    tracker_config = GlobFileTrackerConfig(
        root=loader.get_path('tracker', 'glob', 'root', root=resolver.get_root(), default=resolver.get_root()),
        patterns=load_glob_tracker_patterns_from_config(loader),
        flags=load_glob_tracker_flags_from_config(loader),
    )

    return GlobFileTracker(tracker_config, resolver, static_config)


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


def load_glob_tracker_flags_from_config(loader: ConfigLoader) -> Sequence[str]:
    match flags := loader.get_nested('tracker', 'glob', 'flags'):
        case JsonArray():
            for flag in flags:
                # The actual flags will get validated when constructing the config
                if not isinstance(flags, str):
                    raise ViatConfigError(f'Invalid glob pattern {flag} in tracker.glob.flags')

            return cast('Sequence[str]', flags)

        case None:
            return DEFAULT_GLOB_FLAGS

        case _:
            raise ViatConfigError('The tracker.glob.patterns option must be an array of glob patterns')


def load_git_tracker_from_config(resolver: ViatPathResolver, static_config: ViatVaultStaticConfig, loader: ConfigLoader) -> ViatFileTracker:
    tracker_config = GitFileTrackerConfig(
        repo_root=loader.get_path('tracker', 'git', 'repo_root', root=resolver.get_root(), default=resolver.get_root()),
        revision=loader.get_str('tracker', 'git', 'revision', default=GitFileTrackerConfig.revision),
    )

    return GitFileTracker(tracker_config, resolver, static_config)

