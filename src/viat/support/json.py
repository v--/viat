"""Python type hints for JSON values."""

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable


if TYPE_CHECKING:
    from viat.support.collection_protocols import (
        MappingProtocol,
        MutableMappingProtocol,
        MutableSequenceProtocol,
        SequenceProtocol,
    )


type AtomicJson = bool | float | str | None
"""Type union of atomic JSON types."""


if TYPE_CHECKING:
    @runtime_checkable
    class JsonArray(SequenceProtocol[Any, 'Json'], Protocol):
        """Protocol for immutable JSON arrays.

        The protocol mimics `Sequence[Json]` during type checking.
        At runtime, `JsonArray` is simply an alias for
        [`Sequence`][collections.abc.Sequence].
        """
else:
    JsonArray = Sequence


if TYPE_CHECKING:
    @runtime_checkable
    class JsonObject(MappingProtocol[str, 'Json'], Protocol):
        """Protocol for immutable JSON objects.

        The protocol mimics `Mapping[str, Json]` during type checking.
        At runtime, `JsonArray` is simply an alias for
        [`Mapping`][collections.abc.Mapping].
        """
else:
    JsonObject = Mapping


type Json = AtomicJson | JsonArray | JsonObject
"""Type alias for immutable JSON values."""


if TYPE_CHECKING:
    @runtime_checkable
    class MutableJsonArray(MutableSequenceProtocol[Any, 'MutableJson'], Protocol):
        """Protocol for mutable JSON arrays.

        The protocol mimics `MuableSequence[Json]` during type checking.
        At runtime, `MutableJsonArray` is simply an alias for
        [`MutableSequence`][collections.abc.MutableSequence].
        """
else:
    MutableJsonArray = Sequence


if TYPE_CHECKING:
    @runtime_checkable
    class MutableJsonObject(MutableMappingProtocol[str, 'MutableJson'], Protocol):
        """Protocol for mutable JSON objects.

        The protocol mimics `MutableMapping[str, Json]` during type checking.
        At runtime, `MutableJsonArray` is simply an alias for
        [`MutableMapping`][collections.abc.MutableMapping].
        """
else:
    MutableJsonObject = Mapping


type MutableJson = AtomicJson | JsonArray | MutableJsonArray | JsonObject | MutableJsonObject
"""Type alias for mutable JSON values."""
