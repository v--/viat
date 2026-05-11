import pathlib
from dataclasses import dataclass


@dataclass
class GitFileTrackerConfig:
    """Configuration for the git file tracker."""

    repo_root: pathlib.Path
    """The root of the repository to track files from."""

    revision: str = 'HEAD'
    """The git revision to track files from."""
