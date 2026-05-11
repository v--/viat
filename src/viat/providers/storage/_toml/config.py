import pathlib
from dataclasses import dataclass


@dataclass
class TomlAttributeStorageConfig:
    """Configuration for the TOML file storage."""

    storage_path: pathlib.Path
    """The path to a file for storing attributes.

    The configuration loader sets this to the default value `storage.toml`.
    """

    json_schema_path: pathlib.Path | None = None
    """Path to a JSON schema file.

    We utilize the fact that TOML maps to JSON to enable validation via JSON schemas.

    If empty, we assume no schema.

    The configuration loader (but not the storage itself) uses the default value `schema.json` if it exists.
    """
