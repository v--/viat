"""Protocols upon which viat is built."""
import pathlib
from collections.abc import Iterable, Mapping, MutableMapping
from contextlib import AbstractContextManager
from typing import Protocol

from viat.support.json import JsonT


class ViatFileTracker(Protocol):
    """An abstraction for enumerating and emitting paths.

    It can be a directory walker, a static file list or anything else.
    """

    def iter_paths(self) -> Iterable[pathlib.Path]:
        """Iterate all tracked file paths.

        Returns:
            An iterable of paths in no particular order.
        """

    def is_tracked(self, path: pathlib.Path) -> bool:
        """Check whether a file is being tracked.

        Args:
            path: The file path.
        """

    def validate_tracked(self, path: pathlib.Path) -> None:
        """Validate that a file is being tracked and emit and otherwise emit
        [`ViatUntrackedFileWarning`](viat.exceptions.ViatUntrackedFileWarning).

        Args:
            path: The file path.
        """  # noqa: D205


class ViatAttributeReader(Mapping[str, JsonT]):
    """A scoped attribute reader for a storage entry.

    This is not a protocol because it inherits the Mapping ABC.
    """


class ViatAttributeMutator(MutableMapping[str, JsonT]):
    """A scoped attribute mutator for a storage entry.

    This is not a protocol because it inherits the MutableMapping ABC.
    """


class ViatAttributeStorageConnection(Protocol):
    """An abstraction for managing storage mutators.

    Connection providers may use anything from a simple dictionary to an open database connection.

    Example:
        The following code updates an attribute:

            with conn.get_mutator(path) as mut:
                mut['key'] = 'value'

        Once the context manager exits, the connection validates the update.
    """

    def get_reader(self, path: pathlib.Path | str) -> AbstractContextManager[ViatAttributeReader]:
        """Create a context manager that produces an attribute reader.

        Args:
            path: The path for which to produce the attribute reader for.

        Returns:
            A context manager wrapping a reader.
        """
        ...

    def get_mutator(self, path: pathlib.Path | str) -> AbstractContextManager[ViatAttributeMutator]:
        """Create a context manager that produces an attribute mutator.

        Upon exiting, the context manager must validate the state of the mutator.

        Args:
            path: The path for which to produce the attribute mutator for.

        Returns:
            A context manager wrapping a mutator.
        """
        ...

    def iter_known_paths(self) -> Iterable[pathlib.Path]:
        """Iterate all paths with at least one attribute set.

        Returns:
            An iterable of known paths in no particular order.
        """


class ViatAttributeStorage(AbstractContextManager[ViatAttributeStorageConnection], Protocol):
    """A storage for virtual attributes.

    It is only meant to be used indirectly as a context manager that emits a
    [`ViatAttributeStorageConnection`][..ViatAttributeStorageConnection].

    Upon exiting the context manager, the updates should be committed.

    Example:
        The following code updates an attribute and saves the result:

            with vault.storage as conn, conn.get_mutator(path) as mut:
                mut['key'] = 'value'

        Once the inner context  exits, the connection validates the update.
        Once the outer context manager exits, the storage saves all updates that were made.
    """
