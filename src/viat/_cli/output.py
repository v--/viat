import contextlib
import json
import pathlib
from collections.abc import Generator, Iterable

import click

from viat.exceptions import ViatError, ViatWarning
from viat.support.json import JsonT


@contextlib.contextmanager
def with_cli_exception_handler() -> Generator[None]:
    """Set up an handler that pretty prints viat exceptions."""
    try:
        yield
    except ViatError as err:
        raise click.ClickException(err.get_human_readable_string()) from err


def cli_warning_handler(warning: ViatWarning, stacklevel: int) -> bool:  # noqa: ARG001
    click.echo('Warning: ' + warning.get_human_readable_string(), err=True)
    return True


def print_json_value(value: JsonT, *, raw: bool = False) -> None:
    if raw and isinstance(value, str):
        click.echo(value)
    else:
        click.echo(json.dumps(value))


def print_paths(paths: Iterable[pathlib.Path], *, output_json: bool = False) -> None:
    if output_json:
        print_json_value([path.as_posix() for path in paths])
    else:
        for path in paths:
            click.echo(path.as_posix())
