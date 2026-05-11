"""Protocols that mimic some of the stdlib collection and context manager ABCs.

We only implement a few protocols for type checking of JSON. These protocols are
not used at runtime (even the runtime_checkable decorator is there only for type
checking)

It is not worthwhile for us to accurately reproduce the ABCs with all their base
classes and dependencies, but the result is close enough.

The annotations are based on [typing.pyi] and [contextlib.pyi] from the typeshed.

[typing.pyi]: https://github.com/python/typeshed/blob/main/stdlib/typing.pyi
[contextlib.pyi]: https://github.com/python/typeshed/blob/main/stdlib/contextlib.pyi
"""
# ruff: noqa: D102, D105, PLW1641

from collections.abc import ItemsView, Iterable, Iterator, KeysView, ValuesView
from types import TracebackType
from typing import Protocol, overload, runtime_checkable


@runtime_checkable
class CollectionProtocol[T](Protocol):
    """Protocol that mimics the [`Collection`][collections.abc.Collection] ABC.

    Type Parameters:
        T: The item type of the collection.
    """

    def __iter__(self) -> Iterator[T]: ...
    def __len__(self) -> int: ...
    def __contains__(self, x: T, /) -> bool: ...


@runtime_checkable
class SequenceProtocol[T](CollectionProtocol[T], Protocol):
    """Protocol that mimics the [`Sequence`][collections.abc.Sequence] ABC.

    Type Parameters:
        T: The item type of the sequence.
    """

    # Abstract methods
    @overload
    def __getitem__(self, index: int, /) -> T: ...
    @overload
    def __getitem__(self, index: 'slice[int | None]', /) -> Iterable[T]: ...

    # Mixin methods
    def index(self, value: T, start: int = 0, stop: int = ..., /) -> int: ...
    def count(self, value: T, /) -> int: ...
    def __contains__(self, value: object, /) -> bool: ...
    def __iter__(self) -> Iterator[T]: ...
    def __reversed__(self) -> Iterator[T]: ...


@runtime_checkable
class MutableSequenceProtocol[T](SequenceProtocol[T], Protocol):
    """Protocol that mimics the [`MutableSequence`][collections.abc.MutableSequence] ABC.

    Type Parameters:
        T: The item type of the sequence.
    """

    # Abstract methods
    def insert(self, index: int, value: T, /) -> None: ...
    @overload
    def __getitem__(self, index: int, /) -> T: ...
    @overload
    def __getitem__(self, index: 'slice[int | None]', /) -> Iterable[T]: ...
    @overload
    def __setitem__(self, index: int, value: T, /) -> None: ...
    @overload
    def __setitem__(self, index: 'slice[int | None]', value: Iterable[T], /) -> None: ...
    @overload
    def __delitem__(self, index: int, /) -> None: ...
    @overload
    def __delitem__(self, index: 'slice[int | None]', /) -> None: ...

    # Mixin methods
    def append(self, value: T, /) -> None: ...
    def clear(self) -> None: ...
    def extend(self, values: Iterable[T], /) -> None: ...
    def reverse(self) -> None: ...
    def pop(self, index: int = -1, /) -> T: ...
    def remove(self, value: T, /) -> None: ...
    def __iadd__(self, values: Iterable[T], /) -> Iterable[T]: ...


@runtime_checkable
class MappingProtocol[K, V](CollectionProtocol[K], Protocol):
    """Protocol that mimics the [`Mapping`][collections.abc.Mapping] ABC.

    Type Parameters:
        K: The type of keys.
        V: The type of values.
    """

    # Abstract methods
    def __getitem__(self, key: K, /) -> V: ...

    # Mixin methods
    @overload
    def get(self, key: K, /) -> V | None: ...
    @overload
    def get(self, key: K, default: V, /) -> V: ...
    def items(self) -> ItemsView[K, V]: ...
    def keys(self) -> KeysView[K]: ...
    def values(self) -> ValuesView[V]: ...
    def __contains__(self, key: object, /) -> bool: ...
    def __eq__(self, other: object, /) -> bool: ...


@runtime_checkable
class MutableMappingProtocol[K, V](MappingProtocol[K, V], Protocol):
    """Protocol that mimics the [`MutableMapping`][collections.abc.MutableMapping] ABC.

    Type Parameters:
        K: The type of keys.
        V: The type of values.
    """

    # Abstract methods
    def __setitem__(self, key: K, value: V, /) -> None: ...
    def __delitem__(self, key: K, /) -> None: ...

    # Mixin methods
    def clear(self) -> None: ...
    @overload
    def pop(self, key: K, /) -> V: ...
    @overload
    def pop(self, key: K, default: V, /) -> V: ...
    def popitem(self) -> tuple[K, V]: ...
    @overload
    def setdefault(self: 'MutableMappingProtocol[K, V | None]', key: K, default: None = None, /) -> V | None: ...
    @overload
    def setdefault(self, key: K, default: V, /) -> V: ...
    @overload
    def update(self, m: MappingProtocol[K, V], /) -> None: ...
    @overload
    def update(self: MappingProtocol[str, V], m: MappingProtocol[str, V], /, **kwargs: V) -> None: ...
    @overload
    def update(self, m: Iterable[tuple[K, V]], /) -> None: ...
    @overload
    def update(self: MappingProtocol[str, V], m: Iterable[tuple[str, V]], /, **kwargs: V) -> None: ...
    @overload
    def update(self: MappingProtocol[str, V], /, **kwargs: V) -> None: ...


@runtime_checkable
class AbstractContextManagerProtocol[T](Protocol):
    """Protocol that mimics the [`AbstractContextManager`][contextlib.AbstractContextManager] ABC.

    Type Parameters:
        T: The type of the context.
    """

    def __enter__(self) -> T: ...
    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None, /) -> bool | None: ...
