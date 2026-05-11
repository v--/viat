import subprocess
import importlib.metadata
import io
import pathlib
import re
from inspect import cleandoc
from textwrap import dedent

import click
from click_man.man import ManPage

from viat.cli import viat


ROOT = pathlib.Path(__file__).parent.parent.parent


def build_man_page() -> None:
    version = importlib.metadata.version('viat')
    date_str = extract_date_from_changelog(version)
    pathlib.Path('dist/man').mkdir(parents=True, exist_ok=True)
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

    with open('dist/man/viat.1', 'w') as man_file:
        man_file.writelines(str(click_man_page))
        man_file.write('.SH COMMANDS\n')

        for subcommand in viat.commands.values():
            subctx = click.Context(subcommand, info_name=f'viat {subcommand.name}')
            subcommand_help = subcommand.get_help(subctx) \
                .replace('Usage:', '.TP\n\\fB') \
                .replace('Options:', '.IP\n\\fBOptions:\\fP') \
                .replace('\n\n', '\n.IP\n') \
                .replace('\n  ', '\n.br\n')

            man_file.write(subcommand_help)
            man_file.write('\n')

        man_file.write(
            dedent("""\
                .SH ENVIRONMENT\n
                .TP
                \\fBVIAT_DIR\\fP
                Use a concrete vault directory than searching through the current directory upwards.
                """,
            ),
        )

        man_tutorial = re.sub('```\\w+', '.IP', extracted_readme_usage) \
            .replace('```', '\n.P\n') \
            .replace('`', '"') \
            .replace('\n\n', '\n.P\n') \
            .replace('\n\n', '\n') \
            .replace('\n', '\n.br\n')

        man_file.write('.SH TUTORIAL\n')
        man_file.writelines(man_tutorial)


def build_usage_md() -> None:
    extracted_usage = extract_usage_from_readme(only_cli=False)

    with open('docs/usage.md', 'w') as file:
        file.write('# Usage\n\n')
        file.write(extracted_usage.replace('### ', '## '))


def build_man_md() -> None:
    proc = subprocess.Popen(['groff', '-mandoc', '-Tutf8', '-rLL=87n', 'dist/man/viat.1'], stdout=subprocess.PIPE)
    assert proc.stdout
    rendered = proc.stdout.read().decode('utf-8')
    # The replacement patterns are based on https://stackoverflow.com/a/78367016/2756776
    unescaped = re.sub('\x1B\\[[0-9;]*[JKmsu]', '', rendered)

    with open('docs/man.md', 'w') as file:
        file.write('```troff\n')
        file.write(unescaped)
        file.write('```\n')


def extract_date_from_changelog(version: str) -> str:
    line_start = f'## {version} - '

    with open(ROOT / 'CHANGELOG.md') as file:
        for line in file:
            if line.startswith(line_start):
                return line[len(line_start):].strip()

        raise SystemExit(f'Could not find the build date for version {version}')


def extract_usage_from_readme(only_cli: bool) -> str:
    buffer = io.StringIO()
    in_usage_section = False

    with open(ROOT / 'README.md') as file:
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
