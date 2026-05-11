import json
import pathlib

import click

from viat._cli.group import viat
from viat._cli.output import print_json_value
from viat.exceptions import ViatMalformedDataError
from viat.support.json import JsonObject
from viat.vault import autoload_vault


@viat.command()
@click.argument('path', type=pathlib.Path)
@click.argument('attrs', type=str)
def update(path: pathlib.Path, attrs: str) -> None:
    """Merge the stored attributes for a tracked file with a new JSON object."""
    try:
        parsed = json.loads(attrs)
    except json.JSONDecodeError as err:
        raise ViatMalformedDataError(f'Malformed JSON string {attrs!r}') from err

    if not isinstance(parsed, JsonObject):
        raise ViatMalformedDataError(f'Expected a JSON object, but got {attrs!r}')

    vault = autoload_vault()
    rel_path = vault.normalize_path(path)

    with vault.storage as conn, conn.get_mutator(rel_path) as mut:
        mut.update(parsed)
        updated = dict(mut)

    print_json_value(updated)
