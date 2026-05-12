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
