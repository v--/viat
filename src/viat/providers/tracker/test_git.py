import pathlib
from collections.abc import Sequence

import pygit2
import pytest

from viat.exceptions import ViatFileTrackerError

from .git import GitFileTracker, GitFileTrackerConfig


def git_commit(repo: pygit2.Repository, message: str, parents: Sequence[pygit2.Oid] = []) -> pygit2.Oid:
    ref = repo.index.write_tree()
    author = pygit2.Signature('Test Author', 'author@test.test')
    committer = pygit2.Signature('Test committer', 'committer@test.test')

    return repo.create_commit('HEAD', author, committer, message, ref, parents)


class TestGitFileTrackerIterPaths:
    def test_empty_repository_without_commit(self, temp_directory: pathlib.Path) -> None:
        pygit2.init_repository(temp_directory)
        tracker = GitFileTracker(GitFileTrackerConfig(temp_directory))

        with pytest.raises(ViatFileTrackerError):
            set(tracker.iter_paths())

    def test_empty_commit(self, temp_directory: pathlib.Path) -> None:
        repo = pygit2.init_repository(temp_directory)
        git_commit(repo, 'test')

        tracker = GitFileTracker(GitFileTrackerConfig(temp_directory))
        assert set(tracker.iter_paths()) == set()

    def test_single_commit_with_files(self, temp_directory: pathlib.Path) -> None:
        temp_directory.joinpath('README.md').touch()
        temp_directory.joinpath('src', 'proj').mkdir(parents=True)
        temp_directory.joinpath('src', 'proj', '__init__.py').touch()

        repo = pygit2.init_repository(temp_directory)
        repo.index.add_all()
        git_commit(repo, 'test')

        tracker = GitFileTracker(GitFileTrackerConfig(temp_directory))
        assert set(tracker.iter_paths()) == {
            temp_directory.joinpath('README.md'),
            temp_directory.joinpath('src', 'proj', '__init__.py'),
        }

    def test_track_nonempty_directories(self, temp_directory: pathlib.Path) -> None:
        temp_directory.joinpath('README.md').touch()
        temp_directory.joinpath('src', 'proj').mkdir(parents=True)
        temp_directory.joinpath('src', 'proj', '__init__.py').touch()

        repo = pygit2.init_repository(temp_directory)
        repo.index.add_all()
        git_commit(repo, 'test')

        tracker = GitFileTracker(GitFileTrackerConfig(temp_directory, track_nonempty_directories=True))
        assert set(tracker.iter_paths()) == {
            temp_directory.joinpath('README.md'),
            temp_directory.joinpath('src'),
            temp_directory.joinpath('src', 'proj'),
            temp_directory.joinpath('src', 'proj', '__init__.py'),
        }


class TestGitFileTrackerIsTracked:
    def test_normal_commit(self, temp_directory: pathlib.Path) -> None:
        temp_directory.joinpath('README.md').touch()

        repo = pygit2.init_repository(temp_directory)
        repo.index.add_all()
        git_commit(repo, 'test')

        temp_directory.joinpath('CHANGELOG.md').touch()

        tracker = GitFileTracker(GitFileTrackerConfig(temp_directory))
        assert tracker.is_tracked(temp_directory.joinpath('README.md'))
        assert not tracker.is_tracked(temp_directory.joinpath('CHANGELOG.md'))

    def test_revision_pointer_to_old_commit(self, temp_directory: pathlib.Path) -> None:
        temp_directory.joinpath('README.md').touch()
        temp_directory.joinpath('src', 'proj').mkdir(parents=True)
        temp_directory.joinpath('src', 'proj', '__init__.py').touch()

        repo = pygit2.init_repository(temp_directory)
        repo.index.add_all()
        first_commit = git_commit(repo, 'first')

        temp_directory.joinpath('README.md').unlink()
        repo.index.add_all()
        git_commit(repo, 'second', parents=[first_commit])

        tracker = GitFileTracker(GitFileTrackerConfig(temp_directory, revision=str(first_commit)))
        assert not tracker.is_tracked(temp_directory.joinpath('README.md'))
