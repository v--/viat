from viat.exceptions import ViatIntegrityError
from viat.protocols import ViatFileTracker

from .config import GitFileTrackerConfig


class GitFileTracker(ViatFileTracker):
    """A mock git file tracker implementation that raises an error on init.

    Raises:
        viat.exceptions.ViatIntegrityError: Always
    """

    def __init__(self, _config: GitFileTrackerConfig) -> None:
        raise ViatIntegrityError('pygit2 is required for the git file tracker')
