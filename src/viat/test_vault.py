import pathlib
from textwrap import dedent

import pytest

from viat.exceptions import ViatConfigError, ViatVaultError
from viat.vault import VIAT_SUBDIR, ViatPathResolver, ViatVault, locate_existing_vault_root


class TestVaultInitialize:
    def test_success(self, temp_directory: pathlib.Path) -> None:
        vault = ViatVault.initialize(temp_directory)
        assert isinstance(vault, ViatVault)

    def test_invalid_permissions(self, temp_directory: pathlib.Path) -> None:
        temp_directory.chmod(0o000)

        with pytest.raises(ViatVaultError):
            ViatVault.initialize(temp_directory)

    def test_existing_vault(self, temp_directory: pathlib.Path) -> None:
        temp_directory.joinpath(VIAT_SUBDIR).mkdir()

        with pytest.raises(ViatVaultError):
            ViatVault.initialize(temp_directory)


class TestVault:
    def test_missing_vault(self, temp_directory: pathlib.Path) -> None:
        with pytest.raises(ViatVaultError):
            ViatVault(temp_directory)

    def test_bad_permissions_on_root(self, temp_directory: pathlib.Path) -> None:
        ViatVault.initialize(temp_directory)
        temp_directory.chmod(0o000)

        with pytest.raises(ViatVaultError):
            ViatVault(temp_directory)

    def test_bad_permissions_on_viat(self, temp_directory: pathlib.Path) -> None:
        ViatVault.initialize(temp_directory)

        resolver = ViatPathResolver(temp_directory)
        resolver.get_viat().chmod(0o000)

        with pytest.raises(ViatVaultError):
            ViatVault(temp_directory)


class TestLocateExistingVaultRoot:
    def test_success(self, temp_directory: pathlib.Path) -> None:
        ViatVault.initialize(temp_directory)

        subdir = temp_directory / 'a' / 'b'
        subdir.mkdir(parents=True)

        located_root = locate_existing_vault_root(subdir)
        assert located_root == temp_directory

    def test_success_inside_viat_dir(self, temp_directory: pathlib.Path) -> None:
        initial_vault = ViatVault.initialize(temp_directory)
        located_root = locate_existing_vault_root(initial_vault.resolver.get_viat())
        assert located_root == temp_directory

    def test_invalid(self, temp_directory: pathlib.Path) -> None:
        with pytest.raises(ViatVaultError):
            locate_existing_vault_root(temp_directory)


class TestVaultConfig:
    def test_unreadable_config(self, temp_directory: pathlib.Path) -> None:
        ViatVault.initialize(temp_directory)

        resolver = ViatPathResolver(temp_directory)
        config_path = resolver.get_config('toml')
        config_path.touch()
        config_path.chmod(0o000)

        with pytest.raises(ViatConfigError):
            ViatVault(temp_directory)

    def test_malformed_config(self, temp_directory: pathlib.Path) -> None:
        ViatVault.initialize(temp_directory)

        resolver = ViatPathResolver(temp_directory)
        config_path = resolver.get_config('toml')
        config_path.write_text('gibberish')

        with pytest.raises(ViatConfigError):
            ViatVault(temp_directory)

    def test_config_with_unrecognized_tracker(self, temp_directory: pathlib.Path) -> None:
        ViatVault.initialize(temp_directory)

        resolver = ViatPathResolver(temp_directory)
        config_path = resolver.get_config('toml')
        config_path.write_text(
            dedent("""\
                [tracker]
                provider = 'unrecognized'
                """,
            ),
        )

        with pytest.raises(ViatConfigError):
            ViatVault(temp_directory)

    def test_config_with_invalid_glob_tracker_pattern_type(self, temp_directory: pathlib.Path) -> None:
        ViatVault.initialize(temp_directory)

        resolver = ViatPathResolver(temp_directory)
        config_path = resolver.get_config('toml')
        config_path.write_text(
            dedent("""\
                [tracker.glob]
                patterns = 3
                """,
            ),
        )

        with pytest.raises(ViatConfigError):
            ViatVault(temp_directory)

    def test_config_with_invalid_glob_tracker_flags(self, temp_directory: pathlib.Path) -> None:
        ViatVault.initialize(temp_directory)

        resolver = ViatPathResolver(temp_directory)
        config_path = resolver.get_config('toml')
        config_path.write_text(
            dedent("""\
                [tracker.glob]
                flags = ["INVALID"]
                """,
            ),
        )

        with pytest.raises(ViatConfigError):
            ViatVault(temp_directory)
