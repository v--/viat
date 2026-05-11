"""Tools for tracking which files are known to viat."""

import pathlib
from collections.abc import Iterable
from typing import override

import pygit2

from viat.exceptions import ViatFileTrackerError
from viat.protocols import ViatFileTracker

from .config import GitFileTrackerConfig


class GitFileTracker(ViatFileTracker):
    """The git file tracker.

    Args:
        config: All configuration required for the tracker.
    """

    _repo: pygit2.Repository

    config: GitFileTrackerConfig
    """The configuration used to initialize the tracker."""

    def __init__(self, config: GitFileTrackerConfig) -> None:
        try:
            self._repo = pygit2.Repository(config.repo_root.as_posix())
        except pygit2.GitError as err:
            raise ViatFileTrackerError('The tracker root is not a git repository') from err

        self.config = config

    def _recurse_into_tree(self, tree: pygit2.Tree, base_path: pathlib.Path) -> Iterable[pathlib.Path]:
        for obj in tree:
            match obj:
                case pygit2.Blob():
                    if obj.name:
                        yield base_path / obj.name

                case pygit2.Tree():
                    if obj.name:
                        if self.config.track_nonempty_directories:
                            yield base_path / obj.name

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
    def is_tracked(self, path: pathlib.Path) -> bool:
        relative = path.relative_to(self.config.repo_root)

        try:
            self._repo.blame(relative.as_posix())
        except KeyError:
            return False

        return True
