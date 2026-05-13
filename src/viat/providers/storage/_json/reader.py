import pathlib
from collections.abc import Iterator, Mapping

from viat.exceptions import ViatMissingAttributeError
from viat.protocols import ViatAttributeReader
from viat.support.json import JsonObjectT, JsonT


class JsonAttributeReader(ViatAttributeReader, Mapping[str, JsonT]):
    """A storage reader for JSON objects.

    Args:
        path: The path to which the table corresponds.
        json_object: The object to proxy.
    """

    path: pathlib.Path
    """The path used to initialize the reader."""

    json_object: JsonObjectT
    """The object used to initialize the reader."""

    def __init__(self, path: pathlib.Path, json_object: JsonObjectT) -> None:
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
