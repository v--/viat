"""The glob [`ViatFileTracker`][viat.protocols.ViatFileTracker] provider."""

import pathlib
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import override

from wcmatch import glob

from viat.exceptions import ViatConfigError
from viat.protocols import ViatFileTracker


def validate_wcmatch_flags(flags: str) -> None:
    """Check the validity of wcmatch glob options.

    Args:
        flags: A string whose characters correspond to glob options.

    Raises:
        viat.exceptions.ViatConfigError: If some flag is unrecognized.
    """
    for f in flags:
        if not hasattr(glob, f):
            raise ViatConfigError(f'Unrecognized wcmatch glob flag {f}')


@dataclass
class GlobFileTrackerConfig:
    """Configuration for the glob file tracker.

    Raises:
        viat.exceptions.ViatConfigError: If some flag is unrecognized.
    """

    root: pathlib.Path
    """The root patch for matching relative patterns.

    Relative paths are resolved with respect to the vault root."""

    patterns: Sequence[str]
    """A sequence of wcmatch-flavored glob patterns."""

    flags: str = 'NGB'  # GLOBSTAR (**), NEGATE (!), BRACE ({a,b})
    """A string whose characters correspond to glob options."""

    def __post_init__(self) -> None:  # noqa: D105
        validate_wcmatch_flags(self.flags)


class GlobFileTracker(ViatFileTracker):
    """The default glob file tracker.

    Due to inconsistencies between [glob][] and [fnmatch][] from the standard library,
    we use the more flexible [wcmatch] library.

    [wcmatch]: https://facelessuser.github.io/wcmatch

    Args:
        config: All configuration required for the tracker.
    """

    config: GlobFileTrackerConfig
    """The configuration used to initialize the trackers."""

    def __init__(self, config: GlobFileTrackerConfig) -> None:
        self.config = config

    def _glob_flags(self) -> int:
        return sum(getattr(glob, f) for f in self.config.flags)

    @override
    def iter_paths(self) -> Iterable[pathlib.Path]:
        for raw_path in glob.glob(self.config.patterns, root_dir=self.config.root, flags=self._glob_flags()):
            yield pathlib.Path(raw_path)

    @override
    def is_tracked(self, path: pathlib.Path) -> bool:
        return glob.globmatch(path, self.config.patterns, root_dir=self.config.root, flags=self._glob_flags())
