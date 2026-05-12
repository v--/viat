"""A convenience module for vaults."""

from ._vault import (
    VIAT_SUBDIR,
    ViatPathResolver,
    ViatVault,
    ViatVaultStaticConfig,
    autoload_vault,
    locate_existing_vault_root,
    resolve_enforced_vault_path,
)


__all__ = [
    'VIAT_SUBDIR',
    'ViatPathResolver',
    'ViatVault',
    'ViatVaultStaticConfig',
    'autoload_vault',
    'locate_existing_vault_root',
    'resolve_enforced_vault_path',
]
