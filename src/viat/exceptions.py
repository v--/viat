"""Exceptions (errors and warnings) common to all modules."""
# ruff: noqa: D105

import contextlib
import pathlib
import warnings
from collections.abc import Callable, Generator, MutableSequence


class ViatException(Exception):
    """Generic exception class."""

    def get_human_readable_string(self) -> str:
        """Get a human readable string suitable for e.g. logging."""
        if isinstance(self.__cause__, ViatException):
            return f'{self}. {self.__cause__}.'

        return f'{self}.'


class ValidationExceptionMixin(Exception):  # noqa: N818
    """Mixin for exceptions related to validation."""
    __cause__: BaseException | None

    def get_human_readable_string(self) -> str:
        """Print the reason for which a validation has failed.

        This is usually not a [`ViatException`](..ViatException) subclass,
        so the default implementation would ignore the cause.
        """
        if self.__cause__:
            return f'{self}: {self.__cause__}.'

        return f'{self}.'


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


class ViatMalformedStoredDataError(ValidationExceptionMixin, ViatAttributeStorageError):
    """Error class for malformed data."""

    def get_path(self) -> pathlib.Path:
        """Get the path used to initialize the error."""
        return self.args[0]

    def __str__(self) -> str:
        return f'Malformed data stored for {self.get_path().as_posix()!r}'


class ViatValidationError(ValidationExceptionMixin, ViatAttributeStorageError):
    """Error class for schema validation failure.

    Args:
        path: Path for which the schema is not valid.
    """

    def __init__(self, path: pathlib.Path) -> None:
        super().__init__(path)

    def get_path(self) -> pathlib.Path:
        """Get the path used to initialize the error."""
        return self.args[0]

    def __str__(self) -> str:
        return f'Validation error for {self.get_path().as_posix()!r}'


class ViatMissingAttributeError(ViatAttributeStorageError, KeyError):
    """Error class for missing attributes.

    Args:
        path: Path for which the attribute is missing.
        attr: Name of missing attribute.
    """

    def __init__(self, path: pathlib.Path, attr: str) -> None:
        super().__init__(path, attr)

    def get_path(self) -> pathlib.Path:
        """Get the path used to initialize the error."""
        return self.args[0]

    def get_attr(self) -> pathlib.Path:
        """Get the attribute name used to initialize the error."""
        return self.args[1]

    def __str__(self) -> str:
        return f'Attribute {self.get_attr()!r} has not been set for {self.get_path().as_posix()!r}'


class ViatCliError(ViatError):
    """Error class for the command-line interface."""


class ViatWarning(ViatException, Warning):
    """Generic warnings class."""


class ViatAttributeStorageWarning(ViatWarning):
    """Generic warning class for storage-related issues."""


class ViatUntrackedFileWarning(ViatAttributeStorageWarning):
    """Warning class for untracked files."""

    def get_path(self) -> pathlib.Path:
        """Get the path used to initialize the error."""
        return self.args[0]

    def __str__(self) -> str:
        return f'File {self.get_path().as_posix()!r} is not being tracked'


class ViatStoredDataValidationWarning(ValidationExceptionMixin, ViatAttributeStorageWarning):
    """Warning class for stored data that does not pass validation.

    Args:
        path: Path for which the stored data is not valid.
    """

    def __init__(self, path: pathlib.Path, cause: BaseException | None = None) -> None:
        super().__init__(path)
        self.__cause__ = cause

    def get_path(self) -> pathlib.Path:
        """Get the path used to initialize the error."""
        return self.args[0]

    def __str__(self) -> str:
        return f'Validation error in stored data for {self.get_path().as_posix()!r}'


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


def emit_warning(warning: ViatWarning, stacklevel: int) -> None:
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
