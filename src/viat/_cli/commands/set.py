import json
import pathlib
from typing import TYPE_CHECKING

import click

from viat._cli.group import viat
from viat._cli.output import print_json_value
from viat.exceptions import ViatMalformedDataError
from viat.vault import autoload_vault


if TYPE_CHECKING:
    from viat.support.json import Json


@viat.command('set')
@click.option('-r', '--raw', is_flag=True, help='Treat the value like a string rather than as JSON.')
@click.argument('path', type=pathlib.Path)
@click.argument('attr', type=str)
@click.argument('value', type=str)
def set_(path: pathlib.Path, attr: str, value: str, raw: bool) -> None:
    """Update a stored attribute for a tracked file.

    Unless the --raw parameter is given, we treat the value as JSON.
    """
    parsed_value: Json

    if raw:
        parsed_value = value
    else:
        try:
            parsed_value = json.loads(value)
        except json.JSONDecodeError as err:
            raise ViatMalformedDataError(f'Malformed JSON string {value!r}') from err

    vault = autoload_vault()
    rel_path = vault.normalize_path(path)

    with vault.storage as conn, conn.get_mutator(rel_path) as mut:
        mut[attr] = parsed_value
        updated = dict(mut)

    print_json_value(updated)
