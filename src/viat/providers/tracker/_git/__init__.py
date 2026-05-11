from typing import TYPE_CHECKING

from .config import GitFileTrackerConfig


# This condition is reversed because griffe takes the latest import when collecting symbols for mkdocstrings
if not TYPE_CHECKING:
    try:
        from .real import GitFileTracker
    except ImportError:
        from .mock import GitFileTracker
else:
    from .real import GitFileTracker
