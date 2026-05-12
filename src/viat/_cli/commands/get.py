import pathlib

import click

from viat._cli.group import viat
from viat._cli.output import print_json_value
from viat.vault import autoload_vault


@viat.command()
@click.argument('path', type=pathlib.Path)
@click.argument('attr', type=str)
@click.option('-r', '--raw', is_flag=True, help='Do not quote strings.')
@click.pass_context
def get(ctx: click.Context, path: pathlib.Path, attr: str, raw: bool) -> None:
    """Retrieve a stored attribute for a tracked file."""
    vault = autoload_vault(ctx.obj.vault_config)
    vault.tracker.validate_tracked(path)

    with vault.storage as conn, conn.get_reader(path) as reader:
        print_json_value(reader[attr], raw=raw)

