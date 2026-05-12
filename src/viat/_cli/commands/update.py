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
@click.pass_context
def update(ctx: click.Context, path: pathlib.Path, attrs: str) -> None:
    """Merge the stored attributes for a tracked file with a new JSON object."""
    try:
        parsed = json.loads(attrs)
    except json.JSONDecodeError as err:
        raise ViatMalformedDataError(f'Malformed JSON string {attrs!r}') from err

    if not isinstance(parsed, JsonObject):
        raise ViatMalformedDataError(f'Expected a JSON object, but got {attrs!r}')

    vault = autoload_vault(ctx.obj.vault_config)
    vault.tracker.validate_tracked(path)

    with vault.storage as conn, conn.get_mutator(path) as mut:
        mut.update(parsed)
        updated = dict(mut)

    print_json_value(updated)
