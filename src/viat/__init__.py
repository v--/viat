"""Principal convenience module."""

from .exceptions import (
    ViatAttributeStorageError,
    ViatAttributeStorageWarning,
    ViatError,
    ViatFileTrackerError,
    ViatMalformedStoredDataError,
    ViatMissingAttributeError,
    ViatValidationError,
    ViatVaultError,
    ViatWarning,
)
from .protocols import ViatAttributeMutator, ViatAttributeStorage, ViatAttributeStorageConnection, ViatFileTracker
from .providers.storage import __all__ as storage_all
from .providers.tracker import __all__ as tracker_all
from .vault import ViatVault, autoload_vault


__all__ = [  # noqa: PLE0604
    'autoload_vault',
    'ViatAttributeMutator',
    'ViatAttributeStorage',
    'ViatAttributeStorageConnection',
    'ViatAttributeStorageError',
    'ViatAttributeStorageWarning',
    'ViatError',
    'ViatFileTracker',
    'ViatFileTrackerError',
    'ViatMalformedStoredDataError',
    'ViatMissingAttributeError',
    'ViatValidationError',
    'ViatVault',
    'ViatVaultError',
    'ViatWarning',
    *storage_all,
    *tracker_all,
]
