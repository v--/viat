import pathlib

import click

from viat._cli.group import viat
from viat.exceptions import ViatVaultError
from viat.vault import autoload_vault


@viat.command()
@click.argument('src', type=pathlib.Path)
@click.argument('dest', type=pathlib.Path)
@click.option('-f', '--force', is_flag=True, help='Move even if the destination exists.')
@click.pass_context
def mv(ctx: click.Context, src: pathlib.Path, dest: pathlib.Path, force: bool) -> None:
    """Move a file along with its metadata."""
    if dest.exists() and not force:
        raise ViatVaultError(f'File {dest.as_posix()!r} already exists')

    vault = autoload_vault(ctx.obj.vault_config)
    rel_src_path = vault.normalize_path(src)

    try:
        src.rename(dest)
    except OSError as err:
        raise ViatVaultError(f'Aborting due to file system error: {err}') from err

    rel_dest_path = vault.normalize_path(dest)

    with (
        vault.storage as conn,
        conn.get_mutator(rel_src_path) as src_mut,
        conn.get_mutator(rel_dest_path) as dest_mut,
    ):
        data = dict(src_mut)
        src_mut.clear()
        dest_mut.update(data)
