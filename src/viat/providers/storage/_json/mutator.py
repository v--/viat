import pathlib
from collections.abc import Iterator, MutableMapping

from viat.exceptions import ViatMissingAttributeError
from viat.protocols import ViatAttributeMutator
from viat.support.json import JsonT


class JsonAttributeMutator(ViatAttributeMutator, MutableMapping[str, JsonT]):
    """A storage mutator for JSON objects.

    Args:
        path: The path to which the table corresponds.
        json_object: The object to proxy.
    """

    path: pathlib.Path
    """The path used to initialize the mutator."""

    json_object: MutableMapping[str, JsonT]
    """The object used to initialize the mutator."""

    def __init__(self, path: pathlib.Path, json_object: MutableMapping[str, JsonT]) -> None:
        self.path = path
        self.json_object = json_object

    def __getitem__(self, key: str) -> JsonT:
        try:
            return self.json_object[key]
        except KeyError:
            raise ViatMissingAttributeError(self.path, key) from None

    def __iter__(self) -> Iterator[str]:
        return iter(self.json_object)

    def __len__(self) -> int:
        return len(self.json_object)

    def __setitem__(self, key: str, value: JsonT) -> None:
        self.json_object[key] = value

    def __delitem__(self, key: str) -> None:
        try:
            del self.json_object[key]
        except KeyError:
            raise ViatMissingAttributeError(self.path, key) from None
