"""The implementation for vaults."""
import os
import pathlib

from viat._config import ConfigLoader, load_storage_from_config, load_tracker_from_config
from viat.exceptions import ViatUntrackedFileWarning, ViatVaultError, process_warning
from viat.protocols import ViatAttributeStorage, ViatFileTracker
from viat.support.path_resolver import VIAT_SUBDIR, ViatPathResolver


class ViatVault:
    """The default provider that stores all configuration and data in a `.viat` subdirectory.

    Args:
        root: The root path of the vault.

            To find a vault root from a subdirectory, you can use the [`locate`][.locate] factory method instead.

    Raises:
        viat.exceptions.ViatConfigError: If the vault is misconfigured.
    """

    resolver: ViatPathResolver
    tracker: ViatFileTracker
    storage: ViatAttributeStorage

    @staticmethod
    def initialize(root: pathlib.Path) -> 'ViatVault':
        """Initialize a new vault.

        Args:
            root: The root of the new vault.

        Returns:
            A newly initialized vault

        Raises:
            viat.exceptions.ViatVaultError: If a vault already exists or if its creation fails.
        """
        resolver = ViatPathResolver(root)

        try:
            resolver.get_viat().mkdir(parents=True)
        except PermissionError as err:
            raise ViatVaultError('No permissions to initialize vault here') from err
        except FileExistsError as err:
            raise ViatVaultError('A vault has already been set up here') from err

        resolver.get_config('toml').touch()
        return ViatVault(root)

    @staticmethod
    def locate(path: pathlib.Path) -> 'ViatVault':
        """Traverse the file system until a vault is found.

        Args:
            path: The path to start the search at.

        Returns:
            An initialized vault

        Raises:
            viat.exceptions.ViatVaultError: If no vault is found.
        """
        candidate = path

        while not (candidate / VIAT_SUBDIR).exists() and candidate != candidate.parent:
            candidate = candidate.parent

        if (candidate / VIAT_SUBDIR).exists():
            return ViatVault(candidate)

        raise ViatVaultError('Could not locate vault')

    def __init__(self, root: pathlib.Path) -> None:
        self.resolver = ViatPathResolver(root)

        try:
            self.resolver.get_viat().stat()
        except FileNotFoundError as err:
            raise ViatVaultError(f'Missing {VIAT_SUBDIR} subdirectory') from err
        except OSError as err:
            raise ViatVaultError(f'The {VIAT_SUBDIR} subdirectory cannot be accessed') from err

        if config_loader := ConfigLoader.try_load_toml_file(self.resolver.get_config('toml')):
            if self.resolver.get_config('json').exists():
                raise ViatVaultError(f'Cannot have both config.toml and config.json in the {VIAT_SUBDIR} subdirectory')
        else:
            config_loader = ConfigLoader.try_load_json_file(self.resolver.get_config('json')) or ConfigLoader({})

        self.tracker = load_tracker_from_config(self.resolver, config_loader)
        self.storage = load_storage_from_config(self.resolver, config_loader)

    def normalize_path(self, path: pathlib.Path | str) -> pathlib.Path:
        """Normalize a path so that it can be used with the vault's storage and verify that it is tracked.

        Args:
            path: Any path.

        Returns:
            The resolved path.
        """
        rel_path = self.resolver.relativize(pathlib.Path(path))

        if not self.tracker.is_tracked(rel_path):
            process_warning(ViatUntrackedFileWarning(rel_path), stacklevel=2)

        return rel_path

def autoresolve_vault_path() -> pathlib.Path:
    """Try to resolve the VIAT_DIR path and fall back to the working directory.

    Returns:
        A path where the vault is supposed to be.

    Raises:
        viat.exceptions.ViatCliError: If the resolution fails.
    """
    try:
        return pathlib.Path(os.environ.get('VIAT_DIR') or '.').resolve()
    except OSError as err:
        raise ViatVaultError('Could not resolve path to viat vault') from err


def autoload_vault() -> ViatVault:
    """Try to load a vault without any manual configuration.

    Returns:
        An initialized vault.

    Raises:
        viat.exceptions.ViatCliError: If the loading fails.
    """
    try:
        return ViatVault(autoresolve_vault_path())
    except ViatVaultError as err:
        raise ViatVaultError('Could not load viat vault') from err
