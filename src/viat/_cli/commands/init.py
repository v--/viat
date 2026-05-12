import pathlib

import click

from viat._cli.group import viat
from viat.vault import ViatVault, resolve_enforced_vault_path


@viat.command()
@click.pass_context
def init(ctx: click.Context) -> None:
    """Initialize a new vault."""
    vault_path = resolve_enforced_vault_path() or pathlib.Path.cwd()
    ViatVault.initialize(vault_path, ctx.obj.vault_config)
