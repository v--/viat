# Viat

A tool for managing **vi**rtual file **at**tributes.

The essence of the tool is that the attributes are stored in plain text formats that can be edited and committed to version control. The main unit of operation is a vault, which is determined by `.viat` subdirectory. In the simplest case, this subdirectory contains `config.toml`, `storage.toml` and possibly `schema.json`.

The package is published as [`viat`](https://pypi.org/project/viat/) on PyPI. See the [installation page](./installation) for more details.

For usage, see the [tutorial](./usage) and the [man page](./man). In short, in an empty vault, the command

```shell
viat set file.pdf --raw attr value
```

puts the following into `storage.toml`:

```toml
["file.pdf"]
attr = "value"
```

Determining which files are tracked by Viat is done via [tracker providers](./api/providers/tracker/), while storing the attributes is done via [storage providers](./api/providers/storage/). Both protocols are very general and new providers can easily be added.
