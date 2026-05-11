import contextlib
import json
import pathlib
from collections.abc import Generator, Iterable

import click

from viat.exceptions import (
    MissingAttributeError,
    ViatError,
    ViatException,
    ViatMalformedStoredDataError,
    ViatStoredDataValidationWarning,
    ViatUntrackedFileWarning,
    ViatValidationError,
    ViatWarning,
)
from viat.support.json import Json


def _recursively_join_error_messages(err: ViatException) -> str:
    if isinstance(err.__cause__, ViatException):
        return f'{err}. {get_error_string(err.__cause__)}'

    return f'{err}.'


def _join_error_message_with_cause(message: str, cause: BaseException | None) -> str:
    if cause:
        return f'{message}: {cause}.'

    return message


def get_error_string(err: ViatException) -> str:
    match err:
        case ViatValidationError():
            (path,) = err.args
            return _join_error_message_with_cause(
                f'Validation error for {path.as_posix()!r}',
                err.__cause__,
            )

        case ViatMalformedStoredDataError():
            (path,) = err.args
            return _join_error_message_with_cause(
                f'Malformed data stored for {path.as_posix()!r}',
                err.__cause__,
            )

        case ViatStoredDataValidationWarning():
            (path,) = err.args
            return _join_error_message_with_cause(
                f'Validation error in stored data for {path.as_posix()!r}',
                err.__cause__,
            )

        case ViatUntrackedFileWarning():
            (path,) = err.args
            return f'File {path.as_posix()!r} is not being tracked.'

        case MissingAttributeError():
            path, attr = err.args
            return f'Attribute {attr!r} has not been set for {path.as_posix()!r}.'

        case _:
            return _recursively_join_error_messages(err)


@contextlib.contextmanager
def with_cli_exception_handler() -> Generator[None]:
    """Set up an handler that pretty prints viat exceptions."""
    try:
        yield
    except ViatError as err:
        raise click.ClickException(get_error_string(err)) from err


def cli_warning_handler(warning: ViatWarning, stacklevel: int) -> bool:  # noqa: ARG001
    click.echo('Warning: ' + get_error_string(warning), err=True)
    return True


def print_json_value(value: Json, *, raw: bool = False) -> None:
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
