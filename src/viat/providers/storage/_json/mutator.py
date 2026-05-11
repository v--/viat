import pathlib
from collections.abc import MutableMapping

from viat.exceptions import MissingAttributeError
from viat.protocols import ViatAttributeMutator
from viat.support.json import Json, MutableJsonObject

from .reader import JsonAttributeReader


class JsonAttributeMutator(MutableMapping[str, Json], JsonAttributeReader, ViatAttributeMutator):
    """A storage mutator for JSON objects.

    Args:
        path: The path to which the table corresponds.
        json_object: The object to proxy.
    """

    path: pathlib.Path
    """The path used to initialize the mutator."""

    json_object: MutableJsonObject
    """The object used to initialize the mutator."""

    def __setitem__(self, key: str, value: Json) -> None:
        self.json_object[key] = value

    def __delitem__(self, key: str) -> None:
        try:
            del self.json_object[key]
        except KeyError:
            raise MissingAttributeError(self.path, key) from None
