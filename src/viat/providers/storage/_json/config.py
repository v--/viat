import pathlib
from dataclasses import dataclass


@dataclass
class JsonAttributeStorageConfig:
    """Configuration for the JSON file storage."""

    storage_path: pathlib.Path
    """The path to a file for storing attributes.

    The configuration loader sets this to the default value `storage.json`.
    """

    json_schema_path: pathlib.Path | None = None
    """Path to a JSON schema file.

    If empty, we assume no schema.

    The configuration loader (but not the storage itself) uses the default value `schema.json` if it exists.
    """

    indent: int | str | None = None
    """An indent parameter for Python's JSON writer."""
