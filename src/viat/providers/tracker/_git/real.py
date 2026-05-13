"""Tools for tracking which files are known to viat."""

import pathlib
from collections.abc import Iterable
from typing import override

import pygit2

from viat._vault.config import ViatVaultStaticConfig
from viat._vault.resolver import ViatPathResolver
from viat.exceptions import ViatFileTrackerError
from viat.protocols import ViatFileTracker
from viat.providers.tracker._base_mixin import TrackerBaseMixin

from .config import GitFileTrackerConfig


class GitFileTracker(TrackerBaseMixin, ViatFileTracker):
    """The git file tracker.

    Args:
        config: All configuration required for the tracker.
        resolver: A path resolver used to process incoming paths.
        static_config: Static configuration for the vault.
    """

    config: GitFileTrackerConfig
    """The configuration used to initialize the tracker."""

    resolver: ViatPathResolver | None
    """The resolver used to initialize the storage."""

    static_config: ViatVaultStaticConfig
    """The vault's static configuration."""

    _repo: pygit2.Repository

    def __init__(
        self,
        config: GitFileTrackerConfig,
        resolver: ViatPathResolver | None = None,
        static_config: ViatVaultStaticConfig | None = None,
    ) -> None:
        try:
            self._repo = pygit2.Repository(config.repo_root.as_posix())
        except pygit2.GitError as err:
            raise ViatFileTrackerError('The tracker root is not a git repository') from err

        self.config = config
        self.resolver = resolver
        self.static_config = static_config or ViatVaultStaticConfig()

    def _recurse_into_tree(self, tree: pygit2.Tree, base_path: pathlib.Path) -> Iterable[pathlib.Path]:
        for obj in tree:
            match obj:
                case pygit2.Blob():
                    if obj.name:
                        yield base_path / obj.name

                case pygit2.Tree():
                    if obj.name:
                        yield from self._recurse_into_tree(obj, base_path / obj.name)

    @override
    def iter_paths(self) -> Iterable[pathlib.Path]:
        try:
            ref = self._repo.revparse_single(self.config.revision)
        except KeyError:
            raise ViatFileTrackerError('No git HEAD pointer') from None

        if ref.raw_name:
            pass

        if not isinstance(ref, pygit2.Commit):
            raise ViatFileTrackerError('git HEAD does not point to a commit')

        yield from self._recurse_into_tree(ref.tree, self.config.repo_root)

    @override
    def is_tracked(self, path: pathlib.Path | str) -> bool:
        rel_path = self._resolve_path(path)

        try:
            self._repo.blame(rel_path.as_posix())
        except (KeyError, ValueError):
            return False

        return True
