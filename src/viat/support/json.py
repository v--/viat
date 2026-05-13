"""Python type hints for JSON values.

These initially used a protocol re-implementation of some stdlib collection ABCs (see [1]).
Unfortunately, after going through several compatibility problems with both the corresponding
ABCs and with actual collections, we decided to split the type hints from the classes used for
instance checks.

* Runtime type checking must be done via `isinstance(value, JsonArray)`.
  Using `value: JsonArray` would not allow lists to be assigned (see [2]).

* Static type checking must be done via the annotation `value: JsonArrayT`.
  Using `isinstance(value, JsonArrayT)` produces a `TypeError` (see [3]).

Note that `isinstance(value, JsonArray)` cannot be mimicked using `isinstance(value, Sequence)`
because the latter also matches strings.

Mutable JSON objects introduce additional complications because of the (in)variance of
the type parameters of MutableMapping, so we abandoned them entirely.

We hope that, at some point, Python's type ecosystem is flexible enough to support JSON hints.

[1]: https://github.com/v--/viat/blob/c479d52e662dfeea56913479761532e81813e21f/src/viat/support/collection_protocols.py
[2]: https://github.com/python/mypy/issues/2922
[3]: https://discuss.python.org/t/runtime-type-checking-using-parameterized-types/70173
"""

import abc
from collections.abc import Mapping, Sequence


type AtomicJsonT = bool | float | str | None
"""Type union of atomic JSON types."""


type JsonArrayT = Sequence['JsonT']
"""A type hint for immutable JSON arrays.

This is intended to be used for type hints. For instance checks,
consider using [`JsonArray`][..JsonArray] instead.
"""


class JsonArray(Sequence['JsonT'], abc.ABC):
    """An ABC for immutable JSON arrays.

    This is intended to be used for instance checks. For type hints,
    consider using [`JsonArrayT`][..JsonArrayT] instead.
    """


JsonArray.register(list)


type JsonObjectT = Mapping[str, 'JsonT']
"""A type hint for immutable JSON objects.

This is intended to be used for type hints. For instance checks,
consider using [`JsonObject`][..JsonObject] instead.
"""


class JsonObject(Mapping[str, 'JsonT'], abc.ABC):
    """An ABC for immutable JSON objects.

    This is intended to be used for instance checks. For type hints,
    consider using [`JsonObjectT`][..JsonObjectT] instead.
    """


JsonObject.register(dict)


type JsonT = AtomicJsonT | JsonArrayT | JsonObjectT
"""Type alias for immutable JSON values."""
