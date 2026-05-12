import os
import pathlib

from viat._config import ConfigLoader, load_storage_from_config, load_tracker_from_config
from viat.exceptions import ViatVaultError
from viat.protocols import ViatAttributeStorage, ViatFileTracker

from .config import ViatVaultStaticConfig
from .resolver import VIAT_SUBDIR, ViatPathResolver


class ViatVault:
    """The default provider that stores all configuration and data in a `.viat` subdirectory.

    Args:
        root: The root path of the vault.

            To find a vault root from a subdirectory, you can use the helper
            [`locate_existing_vault_root`][.locate_existing_vault_root].

        static_config: Static configuration for the vault.

    Raises:
        viat.exceptions.ViatConfigError: If the vault is misconfigured.
    """

    resolver: ViatPathResolver
    """A resolver for paths related to the vault."""

    static_config: ViatVaultStaticConfig
    """The vault's static configuration."""

    tracker: ViatFileTracker
    """The vault's tracker."""

    storage: ViatAttributeStorage
    """The vault's storage."""

    @staticmethod
    def initialize(root: pathlib.Path, static_config: ViatVaultStaticConfig | None = None) -> 'ViatVault':
        """Initialize a new vault.

        Args:
            root: The root of the new vault.
            static_config: Static configuration for the vault.

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
        return ViatVault(root, static_config)

    def __init__(self, root: pathlib.Path, static_config: ViatVaultStaticConfig | None = None) -> None:
        self.resolver = ViatPathResolver(root)

        try:
            self.resolver.get_viat().stat()
        except FileNotFoundError as err:
            raise ViatVaultError(f'Missing {VIAT_SUBDIR} subdirectory') from err
        except OSError as err:
            raise ViatVaultError(f'The {VIAT_SUBDIR} subdirectory cannot be accessed') from err

        if config_loader := ConfigLoader.try_load_toml_file(self.resolver.get_config('toml')):
            if self.resolver.get_config('json').exists():
                raise ViatVaultError(f'Cannot have both static_config.toml and static_config.json in the {VIAT_SUBDIR} subdirectory')
        else:
            config_loader = ConfigLoader.try_load_json_file(self.resolver.get_config('json')) or ConfigLoader({})

        self.static_config = static_config or ViatVaultStaticConfig()
        self.tracker = load_tracker_from_config(self.resolver, self.static_config, config_loader)
        self.storage = load_storage_from_config(self.resolver, self.static_config, config_loader)


def resolve_enforced_vault_path() -> pathlib.Path | None:
    """Try to resolve the path enforced using the VIAT_DIR environment variable.

    Returns:
        Either a resolved path or None if the environment variable is not set.

    Raises:
        viat.exceptions.ViatCliError: If the resolution fails.
    """
    if unresolved := os.environ.get('VIAT_DIR'):
        try:
            return pathlib.Path(unresolved).resolve()
        except OSError as err:
            raise ViatVaultError('Could not resolve path to viat vault') from err

    return None


def locate_existing_vault_root(base: pathlib.Path) -> pathlib.Path:
    """Traverse the file system until a vault is found.

    Args:
        base: The path to start the search at.

    Returns:
        A path to an existing vault.

    Raises:
        viat.exceptions.ViatVaultError: If no vault is found.
    """
    candidate = base

    while not (candidate / VIAT_SUBDIR).exists() and candidate != candidate.parent:
        candidate = candidate.parent

    if (candidate / VIAT_SUBDIR).exists():
        return candidate

    raise ViatVaultError('Could not locate vault')


def autoload_vault(static_config: ViatVaultStaticConfig | None = None) -> ViatVault:
    """Try to load a vault without any manual configuration.

    Returns:
        An initialized vault.

    Raises:
        viat.exceptions.ViatCliError: If the loading fails.
    """
    try:
        return ViatVault(
            resolve_enforced_vault_path() or locate_existing_vault_root(pathlib.Path.cwd()),
            static_config=static_config,
        )
    except ViatVaultError as err:
        raise ViatVaultError('Could not load viat vault') from err
