# Configuration

The following are the default options that roughly correspond to an empty `config.toml` file (see the [tracker API reference](./api/providers/tracker/) and [storage API reference](./api/providers/storage/) for greater detail):
```toml
[tracker]
provider = "glob"  # can be set to "git"

[tracker.glob]
root = "."
patterns = []
provider = "NGB"  # See the documentation for wcmatch.glob

[tracker.git]
repo_root = "."
revision = "HEAD"

[storage]
provider = "toml"  # can be set to "json"

[storage.toml]
storage_path = "storage.toml"
json_schema_path = "schema.json"

[storage.json]
storage_path = "storage.json"
json_schema_path = "schema.json"
indent = 0  # The default is null, but TOML disallows null values
```
