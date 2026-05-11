import contextlib
import pathlib
from textwrap import dedent

import pytest
from click.testing import CliRunner

from viat.cli import viat
from viat.support.path_resolver import ViatPathResolver
from viat.vault import ViatVault


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
            patterns = ["README.md"]
            """,
        ),
    )

    resolver.get_root().joinpath('README.md').write_text('# Readme\n')
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
