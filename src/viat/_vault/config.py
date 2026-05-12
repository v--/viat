from dataclasses import dataclass


@dataclass
class ViatVaultStaticConfig:
    """Static (i.e. known before initialization) configuration for the vault."""

    skip_validation: bool = False
    """Skip tracker and schema validation."""

