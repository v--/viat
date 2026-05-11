"""Exceptions (errors and warnings) common to all modules."""
import contextlib
import pathlib
import warnings
from collections.abc import Callable, Generator, MutableSequence


class ViatException(Exception):
    """Generic exception class."""


class ViatError(ViatException):
    """Generic error class."""


class ViatIntegrityError(ViatError):
    """Error class for internal errors."""


class ViatVaultError(ViatError):
    """Generic error class for configurations."""


class ViatConfigError(ViatVaultError):
    """Generic error class for configurations."""


class ViatFileTrackerError(ViatError):
    """Generic error class for trackers."""


class ViatAttributeStorageError(ViatError):
    """Generic error class for storage-related issues."""


class ViatMalformedDataError(ViatAttributeStorageError):
    """Error class for malformed data."""


class ViatMalformedStoredDataError(ViatMalformedDataError):
    """Error class for malformed data already stored.

    Args:
        path: Path for which the stored data is malformed.
    """

    def __init__(self, path: pathlib.Path) -> None:
        super().__init__(path)


class ViatValidationError(ViatAttributeStorageError):
    """Error class for schema validation failure.

    Args:
        path: Path for which the schema is not valid.
    """

    def __init__(self, path: pathlib.Path) -> None:
        super().__init__(path)


class MissingAttributeError(ViatAttributeStorageError, KeyError):
    """Error class for missing attributes.

    Args:
        path: Path for which the attribute is missing.
        attr: Name of missing attribute.
    """

    def __init__(self, path: pathlib.Path, attr: str) -> None:
        super().__init__(path, attr)


class ViatWarning(ViatException, Warning):
    """Generic warnings class."""


class ViatAttributeStorageWarning(ViatWarning):
    """Generic warning class for storage-related issues."""


class ViatStoredDataValidationWarning(ViatAttributeStorageWarning):
    """Warning class for stored data that does not pass validation.

    Args:
        path: Path for which the stored data is not valid.
    """

    def __init__(self, path: pathlib.Path, cause: BaseException | None = None) -> None:
        super().__init__(path)
        self.__cause__ = cause


_warning_handlers: MutableSequence[Callable[[ViatWarning, int], bool | None]] = []


def install_warning_handler(handler: Callable[[ViatWarning, int], bool | None]) -> None:
    """Install a new warning handler.

    Args:
        handler: A function that accepts a warning and stacklevel.

            If its return value is `True`, we do not process the next handlers.
    """
    _warning_handlers.append(handler)


@contextlib.contextmanager
def with_warning_handler(handler: Callable[[ViatWarning, int], bool | None]) -> Generator[None]:
    """Setup a warning handler in a context manager.

    Args:
        handler: A function that accepts a warning and stacklevel.
    """
    _warning_handlers.append(handler)

    try:
        yield
    finally:
        index = _warning_handlers.index(handler)
        del _warning_handlers[index]


def process_warning(warning: ViatWarning, stacklevel: int) -> None:
    """A wrapper around [`warnings.warn`][] that processes intermediate handlers.

    If any of the handlers return `True`, the next ones, including [`warnings.warn`][], are not processed.

    Args:
        warning: The warning to emit.
        stacklevel: A properly incremented stack level passed to the handlers.
    """
    for handler in _warning_handlers:
        if handler(warning, stacklevel + 2):
            return

    warnings.warn(warning, stacklevel=stacklevel + 2)
