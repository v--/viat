from viat._cli.group import viat
from viat.vault import ViatVault, autoresolve_vault_path


@viat.command()
def init() -> None:
    """Initialize a new vault."""
    vault_path = autoresolve_vault_path()
    ViatVault.initialize(vault_path)
