from dataclasses import dataclass

from viat.vault import ViatVaultStaticConfig


@dataclass
class ViatCliSharedState:
    vault_config: ViatVaultStaticConfig
