# Usage

## Command-line usage

Initialize a vault and update file attributes:

    viat init
    viat set photo.jpg origin --raw photo.dmg
    viat update book.pdf '{"genre": "philosophy", "author": "Ludwig Wittgenstein"}'

Refer to `viat(1)` for more details.

## Programmatic usage

The following sets a virtual attribute for `file.md` and saves it in `.viat/storage.toml`:

    vault = Vault.locate('.')

    with vault.storage as conn, conn.get_mutator('photo.jpg') as mut:
        mut['origin'] = 'photo.dmg'
