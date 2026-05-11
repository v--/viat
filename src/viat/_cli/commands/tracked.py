import click

from viat._cli.group import viat
from viat._cli.output import print_paths
from viat.vault import autoload_vault


@viat.command()
@click.option('-j', '--json', 'output_json', is_flag=True, help='Print the list in JSON format.')
@click.option('-n', '--no-data', is_flag=True, help='Print only those paths without any recorded attributes.')
def tracked(output_json: bool, no_data: bool) -> None:
    """Print out the tracked file paths."""
    vault = autoload_vault()

    if no_data:
        with vault.storage as conn:
            known = set(conn.iter_known_paths())
            paths = [path for path in vault.tracker.iter_paths() if path not in known]

        print_paths(paths, output_json=output_json)
    else:
        print_paths(vault.tracker.iter_paths(), output_json=output_json)

