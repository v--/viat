import pathlib

import click

from viat._cli.group import viat
from viat._cli.output import print_json_value
from viat.vault import autoload_vault


@viat.command()
@click.argument('path', type=pathlib.Path)
def get_all(path: pathlib.Path) -> None:
    """Retrieve all stored attributes for a tracked file."""
    vault = autoload_vault()
    rel_path = vault.resolver.relativize(path)

    with vault.storage as conn, conn.get_reader(rel_path) as reader:
        print_json_value(dict(reader))
