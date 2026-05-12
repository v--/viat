from viat._vault.resolver import ViatPathResolver
from viat.exceptions import ViatIntegrityError
from viat.protocols import ViatFileTracker

from .config import GitFileTrackerConfig


class GitFileTracker(ViatFileTracker):
    """A mock git file tracker implementation that raises an error on init.

    Raises:
        viat.exceptions.ViatIntegrityError: Always
    """

    def __init__(self, config: GitFileTrackerConfig, resolver: ViatPathResolver) -> None:  # noqa: ARG002
        raise ViatIntegrityError('pygit2 is required for the git file tracker')
