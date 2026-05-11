import pathlib

import click

from viat._cli.group import viat
from viat._cli.output import print_json_value
from viat.vault import autoload_vault


@viat.command()
@click.argument('path', type=pathlib.Path)
@click.argument('attr', type=str)
@click.option('-r', '--raw', is_flag=True, help='Do not quote strings.')
def get(path: pathlib.Path, attr: str, raw: bool) -> None:
    """Retrieve a stored attribute for a tracked file."""
    vault = autoload_vault()
    rel_path = vault.normalize_path(path)

    with vault.storage as conn, conn.get_reader(rel_path) as reader:
        print_json_value(reader[attr], raw=raw)

