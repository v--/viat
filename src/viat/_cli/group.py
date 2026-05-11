import click

from viat.exceptions import with_warning_handler

from .output import cli_warning_handler, with_cli_exception_handler


@click.group(epilog='See viat(1) for more details.')
@click.version_option()
@click.pass_context
def viat(ctx: click.Context) -> None:
    """A tool for managing virtual file attributes.

    In short, viat allows recording file attributes in a plain text file, by default TOML.
    """
    ctx.with_resource(with_warning_handler(cli_warning_handler))
    ctx.with_resource(with_cli_exception_handler())
