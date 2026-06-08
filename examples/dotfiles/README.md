# Dotfiles management

I tried several dotfiles managers a long time ago, but quickly realized that none of them were flexible enough for me. I wrote the [fish](https://fishshell.com/) scripts provided in [`./bin.common`](./bin.common), whose role I will explain. The main script in `link-dotfiles`; `link-dotfiles-worker` is only a helper.

I will use systemd services as examples.

> [!TIP]
> See the [usage tutorial](https://viat.readthedocs.io/en/stable/usage/) for an outline of how Viat works.

First, note that only the two systemd folders are tracked by Viat:

```console
$ viat tracked
systemd.host.system
systemd.host.user
```

The README and `bin.common` are not tracked because [`.viat/config.toml`](./.viat/config.toml) contains the following:

```toml
[tracker.glob]
patterns = ["*", "!bin.common", "!README.md"]
```

We will later discuss how to link the contents of `bin.common` in `~/.local/bin`, but for now assume that we have added the directory to the `PATH` environment variable.

In order for the `link-dotfiles` script to know what to do, we must specify several attributes for each tracked directory. [`.viat/storage.toml`](./.viat/storage.toml) contains the following:

```toml
["systemd.host.system"]
dest = "/etc/systemd/system"
privileged = true
scopes = ["host"]
strategy = "copy"

["systemd.host.user"]
dest = "$XDG_CONFIG_HOME/systemd/user"
scopes = ["host"]
strategy = "copy"
```

Running `link-dotfiles` should correctly link the contents of these directories, asking for user's permission if anything needs overwriting.

The JSON schema at [`.viat/schema.json`](./.viat/schema.json) ensures that these fields will always have the correct format. The fields for `dotfiles_subdir` are as follows:

* `dest` contains an absolute path the contents of `dotfiles_subdir` should go into. It may contain environment variables.
* `privileged` is a flag that determines whether `sudo` should be used for linking, i.e. if `dotfiles_subdir` contains system-wide or user-specific configurations.
* `scopes` contains a list of environments for which the dotfiles are intended. These are matched against the `hostname` environment variable.
* `strategy` is a bit more subtle, and we discuss all possible values:
  * `"copy"`, as used for the systemd directories, recursively copies all files in `dotfiles_subdir` to the intended destination (only if the destination's hash differs). I use this in limited cases like for systemd, which may have problems reading symlinks.
  * `"root"` creates a symlink from `dest` to `dotfiles_subdir`, e.g. from `~/.config/systemd/user` to `$DOTFILES_DIR/systems.host.user`. This mode is also to be used in limited cases.
  * `"shallow"` is the most basic linking mode, which creates a symlink for each immediate file or subdirectory of `dotfiles_subdir`. We will use this strategy for `bin.common`.
  * `"deep"` is similar, but works recursively. This is the default in [GNU Stow](https://www.gnu.org/software/stow/).

Now that we have discussed how the dotfile directories are configured, let us add a configuration that links the scripts in `bin.common` to `~/.local/bin`:

```console
$ viat set bin.common --raw dest '$HOME/.local/bin'
Warning: File 'bin.common' is not being tracked.
Error: Validation error for 'bin.common': data must contain ['scopes', 'strategy'] properties.
```

We see that Viat works as intended. It emits a warning that the directory is not tracked (and will thus not be fed to `link-dotfiles`), and it produces a validation error. To fix this, `bin.common` needs to be un-ignored in `.viat/config.toml`, and then we must set all attributes at once (or edit `.viat/storage.toml` in an editor like I do):

```console
$ viat update bin.common '{"dest": "$HOME/.local/bin", "scopes": ["host", "other-host"], "strategy": "shallow"}'
{"dest": "$HOME/.local/bin", "scopes": ["host", "other-host"], "strategy": "shallow"}
```

Running `link-dotfiles` now will now also link these new files. The implementation of this script is actually quite short (modulo some setup):

```fish
for line in (viat shell-export)
    eval "export $line"
    set dest (eval echo $dest)

    if echo $scopes | grep --quiet $hostname
        if test -n "$privileged"
            sudo $worker $path $dest $strategy
        else
            $worker $path $dest $strategy
        end
    end
end
```

The `worker` variable is set to the `link-dotfiles-worker` script, which takes care of the linking itself.
