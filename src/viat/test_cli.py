import contextlib
import pathlib
from textwrap import dedent

import pytest
from click.testing import CliRunner

from viat.cli import viat
from viat.exceptions import ViatAttributeStorageError
from viat.vault import ViatPathResolver, ViatVault


@pytest.fixture
def click_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def vault_with_readme(temp_directory: pathlib.Path) -> ViatVault:
    resolver = ViatPathResolver(temp_directory)
    resolver.get_viat().mkdir()

    config_path = resolver.get_config('toml')
    config_path.write_text(
        dedent("""\
            [tracker.glob]
            patterns = ["*.md"]
            """,
        ),
    )

    temp_directory.joinpath('README.md').write_text('# Readme\n')
    return ViatVault(temp_directory)


class TestInit:
    def test_valid(self, temp_directory: pathlib.Path, click_runner: CliRunner) -> None:
        with contextlib.chdir(temp_directory):
            result = click_runner.invoke(viat, ['init'])
            assert result.stdout == ''
            assert result.stderr == ''

    def test_bad_permissions(self, temp_directory: pathlib.Path, click_runner: CliRunner) -> None:
        with contextlib.chdir(temp_directory):
            temp_directory.chmod(0o000)
            result = click_runner.invoke(viat, ['init'])
            assert result.stdout == ''
            assert result.stderr == 'Error: No permissions to initialize vault here.\n'

    def test_existing(self, temp_directory: pathlib.Path, click_runner: CliRunner) -> None:
        ViatVault.initialize(temp_directory)

        with contextlib.chdir(temp_directory):
            result = click_runner.invoke(viat, ['init'])
            assert result.stdout == ''
            assert result.stderr == 'Error: A vault has already been set up here.\n'


class TestGet:
    def test_valid(self, vault_with_readme: ViatVault, click_runner: CliRunner) -> None:
        print(list(vault_with_readme.tracker.iter_paths()))

        with vault_with_readme.storage as conn, conn.get_mutator('README.md') as mut:
            mut['key'] = 'value'

        with contextlib.chdir(vault_with_readme.resolver.get_root()):
            result = click_runner.invoke(viat, ['get', 'README.md', 'key'])
            assert result.stdout == '"value"\n'
            assert result.stderr == ''

    def test_raw(self, vault_with_readme: ViatVault, click_runner: CliRunner) -> None:
        with vault_with_readme.storage as conn, conn.get_mutator('README.md') as mut:
            mut['key'] = 'value'

        with contextlib.chdir(vault_with_readme.resolver.get_root()):
            result = click_runner.invoke(viat, ['get', '--raw', 'README.md', 'key'])
            assert result.stdout == 'value\n'
            assert result.stderr == ''

    def test_untracked_file(self, temp_directory: pathlib.Path, click_runner: CliRunner) -> None:
        ViatVault.initialize(temp_directory)

        resolver = ViatPathResolver(temp_directory)
        config_path = resolver.get_config('toml')
        config_path.write_text(
            dedent("""\
                [tracker.glob]
                include = ['README.md']
                """,
            ),
        )

        resolver.get_root().joinpath('README.md').touch()

        vault_with_readme = ViatVault(temp_directory)

        with vault_with_readme.storage as conn, conn.get_mutator('README.md') as mut:
            mut['key'] = 'value'

        with contextlib.chdir(vault_with_readme.resolver.get_root()):
            result = click_runner.invoke(viat, ['get', 'README.md', 'key'])
            assert result.stdout == '"value"\n'
            assert result.stderr == "Warning: File 'README.md' is not being tracked.\n"

    def test_path_relativization(self, vault_with_readme: ViatVault, click_runner: CliRunner) -> None:
        with vault_with_readme.storage as conn, conn.get_mutator('README.md') as mut:
            mut['key'] = 'value'

        absolute_path = vault_with_readme.resolver.get_root().absolute().joinpath('README.md').as_posix()

        with contextlib.chdir(vault_with_readme.resolver.get_root()):
            result = click_runner.invoke(viat, ['get', absolute_path, 'key'])
            assert result.stdout == '"value"\n'
            assert result.stderr == ''

    def test_missing_attribute(self, vault_with_readme: ViatVault, click_runner: CliRunner) -> None:
        with contextlib.chdir(vault_with_readme.resolver.get_root()):
            result = click_runner.invoke(viat, ['get', 'README.md', 'key'])
            assert result.stdout == ''
            assert result.stderr == "Error: Attribute 'key' has not been set for 'README.md'.\n"

    def test_invalid_stored(self, vault_with_readme: ViatVault, click_runner: CliRunner) -> None:
        with vault_with_readme.storage as conn, conn.get_mutator('README.md') as mut:
            mut['key'] = 'value'

        schema_path = vault_with_readme.resolver.get_viat().joinpath('schema.json')
        schema = dedent("""\
            {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "number"
                    }
                }
            }""",
        )

        schema_path.write_text(schema)

        with contextlib.chdir(vault_with_readme.resolver.get_root()):
            result = click_runner.invoke(viat, ['get', 'README.md', 'key'])
            assert result.stdout == '"value"\n'
            assert result.stderr == "Warning: Validation error in stored data for 'README.md': data.key must be number.\n"

    def test_invalid_stored_with_disabled_validation(self, vault_with_readme: ViatVault, click_runner: CliRunner) -> None:
        with vault_with_readme.storage as conn, conn.get_mutator('README.md') as mut:
            mut['key'] = 'value'

        schema_path = vault_with_readme.resolver.get_viat().joinpath('schema.json')
        schema = dedent("""\
            {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "number"
                    }
                }
            }""",
        )

        schema_path.write_text(schema)

        with contextlib.chdir(vault_with_readme.resolver.get_root()):
            result = click_runner.invoke(viat, ['--skip-validation', 'get', 'README.md', 'key'])
            assert result.stdout == '"value"\n'
            assert result.stderr == ''


class TestGetAll:
    def test_valid(self, vault_with_readme: ViatVault, click_runner: CliRunner) -> None:
        with vault_with_readme.storage as conn, conn.get_mutator('README.md') as mut:
            mut['key1'] = 'value'
            mut['key2'] = 3

        with contextlib.chdir(vault_with_readme.resolver.get_root()):
            result = click_runner.invoke(viat, ['get-all', 'README.md'])
            assert result.stdout == '{"key1": "value", "key2": 3}\n'
            assert result.stderr == ''


class TestSet:
    def test_valid(self, vault_with_readme: ViatVault, click_runner: CliRunner) -> None:
        with contextlib.chdir(vault_with_readme.resolver.get_root()):
            result = click_runner.invoke(viat, ['set', 'README.md', 'key', '"value"'])
            assert result.stdout == '{"key": "value"}\n'
            assert result.stderr == ''

        with vault_with_readme.storage as conn, conn.get_reader('README.md') as reader:
            assert reader['key'] == 'value'

    def test_raw(self, vault_with_readme: ViatVault, click_runner: CliRunner) -> None:
        with contextlib.chdir(vault_with_readme.resolver.get_root()):
            result = click_runner.invoke(viat, ['set', '--raw', 'README.md', 'key', 'value'])
            assert result.stdout == '{"key": "value"}\n'
            assert result.stderr == ''

        with vault_with_readme.storage as conn, conn.get_reader('README.md') as reader:
            assert reader['key'] == 'value'

    def test_invalid_schema(self, vault_with_readme: ViatVault, click_runner: CliRunner) -> None:
        schema_path = vault_with_readme.resolver.get_viat().joinpath('schema.json')
        schema = dedent("""\
            {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "number"
                    }
                }
            }""",
        )

        schema_path.write_text(schema)

        with contextlib.chdir(vault_with_readme.resolver.get_root()):
            result = click_runner.invoke(viat, ['set', 'README.md', 'key', '"value"'])
            assert result.stdout == ''
            assert result.stderr == "Error: Validation error for 'README.md': data.key must be number.\n"


class TestTracked:
    def test_raw_glob(self, vault_with_readme: ViatVault, click_runner: CliRunner) -> None:
        with contextlib.chdir(vault_with_readme.resolver.get_root()):
            result = click_runner.invoke(viat, ['tracked'])
            assert result.stdout == 'README.md\n'
            assert result.stderr == ''

    def test_json_glob(self, vault_with_readme: ViatVault, click_runner: CliRunner) -> None:
        with contextlib.chdir(vault_with_readme.resolver.get_root()):
            result = click_runner.invoke(viat, ['tracked', '--json'])
            assert result.stdout == '["README.md"]\n'
            assert result.stderr == ''

    def test_no_data(self, temp_directory: pathlib.Path, click_runner: CliRunner) -> None:
        resolver = ViatPathResolver(temp_directory)
        resolver.get_viat().mkdir()

        config_path = resolver.get_config('toml')
        config_path.write_text(
            dedent("""\
                [tracker.glob]
                patterns = ["*.md"]
                """,
            ),
        )

        temp_directory.joinpath('README.md').write_text('# Readme\n')
        temp_directory.joinpath('CHANGELOG.md').touch()

        vault = ViatVault(temp_directory)

        with vault.storage as conn, conn.get_mutator('CHANGELOG.md') as mut:
            mut['key'] = 'value'

        with contextlib.chdir(temp_directory):
            result = click_runner.invoke(viat, ['tracked', '--no-data'])
            assert result.stdout == 'README.md\n'
            assert result.stderr == ''


class TestStale:
    def test_raw_glob(self, vault_with_readme: ViatVault, click_runner: CliRunner) -> None:
        with vault_with_readme.storage as conn, conn.get_mutator('CHANGELOG.md') as mut:
            mut['key'] = 'value'

        with contextlib.chdir(vault_with_readme.resolver.get_root()):
            result = click_runner.invoke(viat, ['stale'])
            assert result.stdout == 'CHANGELOG.md\n'
            assert result.stderr == ''


class TestMv:
    def test_move(self, vault_with_readme: ViatVault, click_runner: CliRunner) -> None:
        with vault_with_readme.storage as conn, conn.get_mutator('README.md') as mut:
            mut['key'] = 'value'

        with contextlib.chdir(vault_with_readme.resolver.get_root()):
            result = click_runner.invoke(viat, ['mv', 'README.md', 'CHANGELOG.md'])
            assert result.stdout == ''
            assert result.stderr == ''

        with vault_with_readme.storage as conn:
            with pytest.raises(ViatAttributeStorageError):  # noqa: SIM117
                with conn.get_reader('README.md') as reader:
                    assert reader['key']

            with conn.get_reader('CHANGELOG.md') as reader:
                assert reader['key'] == 'value'

    def test_move_to_existing(self, vault_with_readme: ViatVault, click_runner: CliRunner) -> None:
        readme = vault_with_readme.resolver.get_root().joinpath('README.md')
        changelog = vault_with_readme.resolver.get_root().joinpath('CHANGELOG.md')
        changelog.touch()

        with contextlib.chdir(vault_with_readme.resolver.get_root()):
            result = click_runner.invoke(viat, ['mv', 'README.md', 'CHANGELOG.md'])
            assert result.stdout == ''
            assert result.stderr == "Error: File 'CHANGELOG.md' already exists.\n"

        assert readme.exists()
        assert changelog.read_text() == ''

    def test_force_move_to_existing(self, vault_with_readme: ViatVault, click_runner: CliRunner) -> None:
        readme = vault_with_readme.resolver.get_root().joinpath('README.md')
        readme_text = readme.read_text()
        changelog = vault_with_readme.resolver.get_root().joinpath('CHANGELOG.md')
        changelog.touch()

        with contextlib.chdir(vault_with_readme.resolver.get_root()):
            result = click_runner.invoke(viat, ['mv', '--force', 'README.md', 'CHANGELOG.md'])
            assert result.stdout == ''
            assert result.stderr == ''

        assert not readme.exists()
        assert changelog.read_text() == readme_text

    def test_error_recovery(self, vault_with_readme: ViatVault, click_runner: CliRunner) -> None:
        readme = vault_with_readme.resolver.get_root().joinpath('README.md')
        changelog = vault_with_readme.resolver.get_root().joinpath('CHANGELOG.md')
        changelog.mkdir()

        with contextlib.chdir(vault_with_readme.resolver.get_root()):
            result = click_runner.invoke(viat, ['mv', '--force', 'README.md', 'CHANGELOG.md'])
            assert result.stdout == ''
            assert result.stderr == "Error: Aborting due to file system error: [Errno 21] Is a directory: 'README.md' -> 'CHANGELOG.md'.\n"

        assert readme.exists()


class TestRm:
    def test_remove(self, vault_with_readme: ViatVault, click_runner: CliRunner) -> None:
        readme = vault_with_readme.resolver.get_root().joinpath('README.md')

        with vault_with_readme.storage as conn, conn.get_mutator('README.md') as mut:
            mut['key'] = 'value'

        with contextlib.chdir(vault_with_readme.resolver.get_root()):
            result = click_runner.invoke(viat, ['rm', 'README.md'])
            assert result.stdout == ''
            assert result.stderr == ''

        assert not readme.exists()

        with pytest.raises(ViatAttributeStorageError):  # noqa: SIM117
            with vault_with_readme.storage as conn, conn.get_reader('README.md') as reader:
                assert reader['key']

    def test_error_recovery(self, vault_with_readme: ViatVault, click_runner: CliRunner) -> None:
        dir_path = vault_with_readme.resolver.get_root().joinpath('dir.md')
        dir_path.mkdir()

        with vault_with_readme.storage as conn, conn.get_mutator('dir.md') as mut:
            mut['key'] = 'value'

        with contextlib.chdir(vault_with_readme.resolver.get_root()):
            result = click_runner.invoke(viat, ['rm', 'dir.md'])
            assert result.stdout == ''
            assert result.stderr == "Error: Aborting due to file system error: [Errno 21] Is a directory: 'dir.md'.\n"

        assert dir_path.exists()

        with vault_with_readme.storage as conn, conn.get_reader('dir.md') as reader:
            assert reader['key'] == 'value'
