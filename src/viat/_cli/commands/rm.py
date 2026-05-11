import pathlib

import click

from viat._cli.group import viat
from viat.exceptions import ViatVaultError
from viat.vault import autoload_vault


@viat.command()
@click.argument('path', type=pathlib.Path)
def rm(path: pathlib.Path) -> None:
    """Remove a file along with its metadata."""
    vault = autoload_vault()
    rel_path = vault.normalize_path(path)

    try:
        path.unlink()
    except OSError as err:
        raise ViatVaultError(f'Aborting due to file system error: {err}') from err

    with vault.storage as conn, conn.get_mutator(rel_path) as mut:
        mut.clear()
