import json
import re
import shlex

import click

from viat._cli.group import viat
from viat.exceptions import ViatCliError
from viat.vault import autoload_vault


def is_valid_variable_name(name: str) -> bool:
    """Check whether a candidate string is a valid variable name for generic shells.

    Obviously valid variable names depend on the shell, but symbols and non-Latin letters
    are generally not supported.
    """
    return re.fullmatch('[a-zA-Z_][a-zA-Z_0-9]*', name) is not None


@viat.command()
@click.pass_context
@click.option('--path-var', type=str, default='path', help="Name of the variable storing the file's path.")
def shell_export(ctx: click.Context, path_var: str) -> None:
    """Print the attributes for all tracked files in a table suitable for shell scripting.

    We list only the attributes that correspond to valid variable names according to [a-zA-Z_][a-zA-Z_0-9]*.

    \b
    Example:
        path=path1 key1=value11 key2=value2
        path=path2 key1=value21 key2=value22
    """  # noqa: D301
    if not is_valid_variable_name(path_var):
        raise ViatCliError(f'As a precaution, we disallow the string {path_var!r} as a variable.')

    cumulative_exported = set[str]()
    vault = autoload_vault(ctx.obj.vault_config)

    with vault.storage as conn:
        for path in vault.tracker.iter_paths():
            click.echo(f'{path_var}={shlex.quote(path.as_posix())}', nl=False)
            exported = set[str]()

            with conn.get_reader(path) as reader:
                for key, value in reader.items():
                    if not is_valid_variable_name(key):
                        continue

                    exported.add(key)
                    cumulative_exported.add(key)

                    value_str = shlex.quote(value if isinstance(value, str) else json.dumps(value))
                    click.echo(f' {key}={value_str}', nl=False)

            for key in cumulative_exported.difference(exported):
                click.echo(f' {key}=', nl=False)

            click.echo('', nl=True)
