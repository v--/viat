import io
import re
import subprocess
from inspect import cleandoc
from textwrap import dedent
from typing import TextIO, cast

import click
from click_man.man import ManPage

from viat.cli import viat

from .paths import MAN_FILE, ROOT


def write_man_page(sink: TextIO) -> None:
    version, date_str = extract_version_and_date_from_changelog()
    extracted_readme_usage = extract_usage_from_readme(only_cli=True)

    # The following code is an variation of the generate_man_page function from
    #   https://github.com/click-contrib/click-man/blob/master/click_man/core.py
    assert viat.help
    ctx = click.Context(viat, info_name='viat')
    click_man_page = ManPage(ctx.command_path)
    click_man_page.version = version
    click_man_page.short_help = viat.get_short_help_str()
    click_man_page.description = cleandoc(viat.help)
    click_man_page.synopsis = ' '.join(viat.collect_usage_pieces(ctx))
    click_man_page.options = [
        x.get_help_record(ctx)
        for x in ctx.command.params
        if isinstance(x, click.Option)
    ]
    click_man_page.date = date_str

    sink.writelines(str(click_man_page))
    sink.write('.SH COMMANDS\n')

    for subcommand in viat.commands.values():
        subctx = click.Context(subcommand, info_name=f'viat {subcommand.name}')
        subcommand_help = subcommand.get_help(subctx) \
            .replace('Usage:', '.TP\n\\fB') \
            .replace('Options:', '.IP\n\\fBOptions:\\fP') \
            .replace('\n\n', '\n.IP\n') \
            .replace('\n  ', '\n.br\n')

        sink.write(subcommand_help)
        sink.write('\n')

    sink.write(
        dedent("""\
            .SH ENVIRONMENT
            .TP
            \\fBVIAT_DIR\\fP
            Use a concrete vault directory than searching through the current directory upwards.
            """,
        ),
    )

    man_tutorial = re.sub(
            r'```\w+',
            '.IP',
            re.sub(r'#### (?P<title>.*)', lambda match: '\\fB' + cast('str', match.group('title').upper()), extracted_readme_usage),
        ) \
        .replace('```', '\n.P\n') \
        .replace('`', '"') \
        .replace('\n\n', '\n.P\n') \
        .replace('\n\n', '\n') \
        .replace('\n', '\n.br\n')

    sink.write('.SH TUTORIAL\n')
    sink.writelines(man_tutorial)


def build_man_page() -> None:
    MAN_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(MAN_FILE, 'w', encoding='utf-8') as man_file:
        write_man_page(man_file)


def write_man_md(sink: TextIO) -> None:
    buffer = io.StringIO()
    write_man_page(buffer)

    proc = subprocess.run(
        ['groff', '-mandoc', '-Tutf8', '-rLL=87n'],
        stdout=subprocess.PIPE,
        input=buffer.getvalue(),
        encoding='utf-8',
        check=True,
    )

    # The replacement patterns are based on https://stackoverflow.com/a/78367016/2756776
    # ruff: ignore[unraw-re-pattern]
    unescaped = re.sub('\x1B\\[[0-9;]*[JKmsu]', '', proc.stdout)

    sink.write('```\n')
    sink.write(unescaped)
    sink.write('```\n')


def write_usage_md(sink: TextIO) -> None:
    extracted_usage = extract_usage_from_readme(only_cli=False)

    adapted_usage = extracted_usage \
        .replace('### ', '## ') \
        .replace('#### ', '### ') \
        .replace('refer to the [online documentation](https://viat.readthedocs.io/) or to the man page', 'refer to the man page')

    sink.write(adapted_usage)


def extract_version_and_date_from_changelog() -> tuple[str, str]:
    with open(ROOT / 'CHANGELOG.md', encoding='utf-8') as file:
        for line in file:
            if match := re.match(r'## (?P<version>[\d.]+) - (?P<date>[\d-]+)', line):
                return match.group('version'), match.group('date')

        raise SystemExit('Could not determine the version and date from the changelog')


def extract_usage_from_readme(only_cli: bool) -> str:
    buffer = io.StringIO()
    in_usage_section = False

    with open(ROOT / 'README.md', encoding='utf-8') as file:
        for line in file:
            if in_usage_section:
                if line.startswith('### ' if only_cli else '## '):
                    buffer.seek(0)
                    return buffer.read().strip()

                buffer.write(line)

            elif line == ('### Command-line usage\n' if only_cli else '## Usage\n'):
                in_usage_section = True

    buffer.seek(0)
    return buffer.read().strip()
