# Installation

The [`viat` PyPI package](https://pypi.org/project/viat/) contains the core programmatic API.

The command-line interface requires the `cli` extra, while the git tracker requires the `git` extra.

To install the `viat` executable for the current user, you can use [`pipx`](https://pipx.pypa.io) or [`uv`](https://docs.astral.sh/uv/):
```shell
pipx install viat[cli]
uv tool install viat[cli]
```
