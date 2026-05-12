"""The TOML [`ViatAttributeStorage`][viat.protocols.ViatAttributeStorage] provider, based on the JSON provider."""

from ._toml import (
    TomlAttributeStorage,
    TomlAttributeStorageConfig,
)


__all__ = [
    'TomlAttributeStorage',
    'TomlAttributeStorageConfig',
]
