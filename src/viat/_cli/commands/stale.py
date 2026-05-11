import click

from viat._cli.group import viat
from viat._cli.output import print_paths
from viat.vault import autoload_vault


@viat.command()
@click.option('-j', '--json', 'output_json', is_flag=True, help='Print the list in JSON format.')
def stale(output_json: bool) -> None:
    """Print out the paths with storage entries that are not tracked."""
    vault = autoload_vault()

    with vault.storage as conn:
        stale_paths = [path for path in conn.iter_known_paths() if not vault.tracker.is_tracked(path)]

    print_paths(stale_paths, output_json=output_json)


