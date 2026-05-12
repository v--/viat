import pathlib


VIAT_SUBDIR = '.viat'
"""The name of the default viat subdirectory."""


class ViatPathResolver:
    """The path resolver for the [`ViatVault`](viat.vault.ViatVault).

    Args:
        root: The root path of the vault.

            To find a vault root from a subdirectory, you can use the [`locate`][.locate] factory method instead.

    Raises:
        viat.exceptions.ViatConfigError: If the vault is misconfigured.
    """

    _root: pathlib.Path

    def __init__(self, root: pathlib.Path) -> None:
        self._root = root

    def get_root(self) -> pathlib.Path:
        """The root directory of the vault."""
        return self._root

    def get_viat(self) -> pathlib.Path:
        """The root directory of the vault."""
        return self._root / VIAT_SUBDIR

    def get_config(self, ext: str) -> pathlib.Path:
        """The root directory of the vault."""
        return self._root / VIAT_SUBDIR / f'config.{ext}'

    def relativize(self, path: pathlib.Path) -> pathlib.Path:
        """Relativize a path so that it can be used with an attribute storage.

        Args:
            path: The path to relativize. If it is already relative, it is left as-is.
        """
        try:
            return path.relative_to(self._root)
        except ValueError:
            return path
