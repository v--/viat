#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "viat >= 0.10.3",
#     "notebook[bibtools] @ https://github.com/v--/notebook.git",
# ]
# ///

import pathlib
from collections.abc import Iterable

import click
from notebook.commands.bibtools.file import read_entries

from viat import ViatAttributeStorageConnection, autoload_vault


def iter_stored_refs(conn: ViatAttributeStorageConnection) -> Iterable[tuple[str, pathlib.Path]]:
    for known_path in conn.iter_known_paths():
        with conn.get_reader(known_path) as reader:
            entry_name = reader['ref']

            if not isinstance(entry_name, str):
                raise TypeError(f'Invalid entry name {entry_name!r}')

            yield entry_name, known_path


if __name__ == '__main__':
    vault = autoload_vault()

    with open(vault.resolver.get_viat() / 'index.bib', encoding='utf-8') as file:
        entries = list(read_entries(file))

    with vault.storage as conn:
        bibtex_refs = frozenset(entry.entry_name for entry in entries)
        viat_known_ref_map = dict(iter_stored_refs(conn))
        viat_refs = frozenset(viat_known_ref_map.keys())

        for bibtex_ref in bibtex_refs.difference(viat_refs):
            click.echo(f'No known file corresponds to the BibTeX ref {bibtex_ref!r}.')

        for bibtex_ref in viat_refs.difference(bibtex_refs):
            file_path = viat_known_ref_map[bibtex_ref]
            click.echo(f'Missing BibTeX ref {bibtex_ref!r} for file {file_path.name!r}.')

            if not vault.tracker.is_tracked(file_path):
                click.echo(f'The file {file_path.name!r} has Viat metadata stored, but is not tracked by Viat.')
