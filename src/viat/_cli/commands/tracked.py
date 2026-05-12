import click

from viat._cli.group import viat
from viat._cli.output import print_paths
from viat.vault import autoload_vault


@viat.command()
@click.option('--json', '-j', 'output_json', is_flag=True, help='Print the list in JSON format.')
@click.option('--no-data', is_flag=True, help='Print only those paths without any recorded attributes.')
@click.pass_context
def tracked(ctx: click.Context, output_json: bool, no_data: bool) -> None:
    """Print out the tracked file paths."""
    vault = autoload_vault(ctx.obj.vault_config)

    if no_data:
        with vault.storage as conn:
            known = set(conn.iter_known_paths())
            paths = [path for path in vault.tracker.iter_paths() if path not in known]

        print_paths(paths, output_json=output_json)
    else:
        # Open the context manager just to validate the schema
        with vault.storage:
            pass

        print_paths(vault.tracker.iter_paths(), output_json=output_json)

