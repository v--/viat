"""Principal convenience module."""

from .exceptions import (
    MissingAttributeError,
    ViatAttributeStorageError,
    ViatAttributeStorageWarning,
    ViatError,
    ViatFileTrackerError,
    ViatMalformedStoredDataError,
    ViatValidationError,
    ViatVaultError,
    ViatWarning,
)
from .protocols import ViatAttributeMutator, ViatAttributeStorage, ViatAttributeStorageConnection, ViatFileTracker
from .providers.storage import __all__ as storage_all
from .providers.tracker import __all__ as tracker_all
from .vault import ViatVault


__all__ = [  # noqa: PLE0604
    *tracker_all,
    *storage_all,
    'ViatVault',
    'ViatAttributeMutator',
    'ViatAttributeStorage',
    'ViatFileTracker',
    'ViatAttributeStorageConnection',
    'ViatError',
    'ViatFileTrackerError',
    'ViatAttributeStorageError',
    'ViatVaultError',
    'ViatWarning',
    'ViatAttributeStorageWarning',
    'ViatMalformedStoredDataError',
    'ViatValidationError',
    'MissingAttributeError',
]
