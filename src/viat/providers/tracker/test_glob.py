import pathlib

from .glob import GlobFileTracker, GlobFileTrackerConfig


class TestGlobFileTrackerIterPaths:
    def test_no_patterns(self, temp_directory: pathlib.Path) -> None:
        tracker = GlobFileTracker(GlobFileTrackerConfig(temp_directory, patterns=[]))
        assert set(tracker.iter_paths()) == set()

    def test_fixed_file_pattern(self, temp_directory: pathlib.Path) -> None:
        temp_directory.joinpath('README.md').touch()
        tracker = GlobFileTracker(GlobFileTrackerConfig(temp_directory, patterns=['README.md']))
        assert set(tracker.iter_paths()) == {pathlib.Path('README.md')}

    def test_absolute_fixed_file_pattern(self, temp_directory: pathlib.Path) -> None:
        readme = temp_directory.joinpath('README.md')
        readme.touch()
        subdir = temp_directory.joinpath('subdir')
        subdir.mkdir()

        tracker = GlobFileTracker(GlobFileTrackerConfig(subdir, patterns=[readme.as_posix()]))
        assert set(tracker.iter_paths()) == {readme}

    def test_wildcard_pattern(self, temp_directory: pathlib.Path) -> None:
        temp_directory.joinpath('a').mkdir()
        temp_directory.joinpath('a', 'b').touch()
        tracker = GlobFileTracker(GlobFileTrackerConfig(temp_directory, patterns=['*/b']))
        assert set(tracker.iter_paths()) == {pathlib.Path('a/b')}

    def test_nested_wildcard_pattern(self, temp_directory: pathlib.Path) -> None:
        temp_directory.joinpath('a').mkdir()
        temp_directory.joinpath('a', 'b').touch()
        tracker = GlobFileTracker(GlobFileTrackerConfig(temp_directory, patterns=['*/b']))
        assert set(tracker.iter_paths()) == {pathlib.Path('a/b')}

    def test_doubly_nested_wildcard_pattern(self, temp_directory: pathlib.Path) -> None:
        temp_directory.joinpath('a', 'b').mkdir(parents=True)
        temp_directory.joinpath('a', 'b', 'c').touch()

        shallow_tracker = GlobFileTracker(GlobFileTrackerConfig(temp_directory, patterns=['*/c']))
        assert set(shallow_tracker.iter_paths()) == set()

        nested_tracker = GlobFileTracker(GlobFileTrackerConfig(temp_directory, patterns=['**/c']))
        assert set(nested_tracker.iter_paths()) == {pathlib.Path('a/b/c')}
