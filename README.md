# Viat

A tool for managing **vi**rtual file **at**tributes.

Viat allows recording file attributes in a plain text file. The main unit of operation is a vault, which is determined by `.viat` subdirectory. In the simplest case, this subdirectory contains `config.toml`, `storage.toml` and possibly `schema.json`.

In short, in an empty vault, the command

```shell
viat set file.pdf --raw attr value
```

puts the following into `storage.toml`:

```toml
[file.pdf]
attr = "value"
```

## Table of contents

* [Usage](#usage)
* [Installation](#installation)
* [Motivation](#motivation)

See also the [documentation on ReadTheDocs](https://viat.readthedocs.io/)

## Usage

We give a usage tutorial here; refer to the [online documentation](https://viat.readthedocs.io/) or to the man page `viat(1)` for more details.

### Command-line usage

First, a vault must be initialized:

```shell
viat init
```

The vault is determined by a `.viat` subfolder that contains `config.toml` and `storage.toml` files (JSON is also supported for both). We can immediately set attributes for any file on the file system:

```shell
$ viat update tractatus.pdf '{"author": "Ludwig Wittgenstein", "year": 1921}'
Warning: File 'tractatus.pdf' is not being tracked.
{"author": "Ludwig Wittgenstein", "year": 1921}
```

All stored attributes for the file get printed; in this case the only stored attributes are those we have just added. We also get a warning saying that the vault's tracker does not know about this file.

The role of the tracker is to enumerate the files that are explicitly tracked by the vault. The default glob-based tracking provider requires explicit patterns. We can track all PDF files in the root of the vault using the following configuration:

```toml
[tracker.glob]
patterns = ["*.pdf"]
```

With this, we can add new properties without warnings:

```shell
$ viat set tractatus.pdf rating 4
{"author": "Ludwig Wittgenstein", "year": 1921, "rating": 4}
```

The above worked because "true" is a valid JSON value; if we were to set a string instead, we would have to escape it in quotes, which is inconvenient. Instead, we can treat the value as a string by passing the `--raw` flag:

```shell
$ viat set --raw tractatus.pdf publisher 'Annalen der Naturphilosophie'
...
```

It makes sense to utilize JSON schemas. Let us add the following to `.viat/schema.json`:

```json
{
  "type":"object",
  "properties": {
    "year": {"type": "number"}
  }
}
```

Now we can no longer set the year to anything that is not a number:

```shell
$ viat set tractatus.pdf --raw year string
Error: Validation error for 'tractatus.pdf': data.year must be number.
```

The essence of the tool is that the attributes are stored in plain text formats that can be edited committed to version control. For example, `.viat/storage.toml` should now look as follows:

```toml
["tractatus.pdf"]
author = "Ludwig Wittgenstein"
year = 1921
rating = 4
publisher = "Annalen der Naturphilosophie"
```

If we manually change the year to "string", we will get a warning when loading the vault:

```shell
$ viat get tractatus.pdf rating
Warning: Validation error in stored data for 'tractatus.pdf': data.year must be number.
4
```

If we move `tractatus.pdf` to `book.pdf`, viat will no longer know about it:

```shell
$ viat get book.pdf rating
Warning: File 'book.pdf' is not being tracked.
Error: Attribute 'rating' has not been set for 'book.pdf'.
```

Such discrepancies can be determined relatively easily:

```bash
$ viat stale
tractatus.pdf
$ viat tracked --no-data
book.pdf
```

For such cases, we provide the helpers `viat mv` and `viat rm`, but otherwise avoid being too clever.

### Programmatic usage

The programmatic usage is straightforward enough because of the [API reference](https://viat.readthedocs.io/). Here is a brief continuation of the above example:

```python
vault = autoload_vault()

assert vault.tracker.is_tracked('tractatus.pdf')

# This context manager validates and writes the file upon exiting.
# If no mutators have been used, no validation and writing is performed.
with vault.storage as conn:
    # The inner lock-based context managers allow either read-only or read-write operations.

    # The following only reads:
    with conn.get_reader('tractatus.pdf') as reader:
        print(mut['year'])

    # The following only writes (but can obviously be used for reading):
    with conn.get_mutator('tractatus.pdf') as mut:
        mut['year'] = 1921
```

## Motivation

When managing lots of files, there comes a point when metadata needs to be attached to them somehow.

* Different file systems offer [extended file attributes](https://en.wikipedia.org/wiki/Extended_file_attributes). Unfortunately, poor software support reduces their utility. For example, `curl --xattr <url>` will record some attributes, but they will be lost on copy (with GNU `cp` at least) and will not be tracked by git.

* [git attributes](https://git-scm.com/docs/gitattributes) are obviously supported by git, but other tools have to consult git in order to use them. Furthermore, there is no convenient mechanism for setting git attributes.

* XMP ([extensible metadata platform](https://developer.adobe.com/xmp/docs/)) files are designed to be used by arbitrary tools and can be easily tracked using version control, but are cumbersome to manage.

Perhaps I am missing some other approaches, but at this point it should be clear that there is no convenient way to manage file metadata. A long time ago I wrote a small script that tracked "virtual" attributes across a directory by putting them into a single JSON file. At some point I decided to refine the script, and so viat was born.

## Installation

The [`viat` PyPI package](https://pypi.org/project/viat/) contains the core programmatic API.

The command-line interface requires the `cli` extra, while the git tracker requires the `git` extra.

To install the `viat` executable for the current user, you can use [`pipx`](https://pipx.pypa.io) or [`uv`](https://docs.astral.sh/uv/):
```shell
pipx install viat[cli]
uv tool install viat[cli]
```

To install from GitHub, you must use the following:

```shell
uv tool install viat --from git+https://github.com/v--/viat[cli]
```

Sometimes a particular feature branch need to be tested. For installing a fixed revision (i.e. common/branch/tag), the following should work (if `extra-name` is needed, use `viat@rev[extra-name]`):

```shell
uv tool install viat --from git+https://github.com/v--/viat@rev
```
