# Installation

The [`viat` PyPI package](https://pypi.org/project/viat/) contains the core programmatic API.

To install the `viat` executable for the current user, you can use [`pipx`](https://pipx.pypa.io):

```shell
pipx install viat
```

or [`uv`](https://docs.astral.sh/uv/):

```shell
uv tool install viat
```

The [git tracker](./api/providers/tracker/#viat.providers.tracker.GitFileTracker) requires the `git` extra.

For installation from source, see the [repository README](https://github.com/v--/viat#installation).
