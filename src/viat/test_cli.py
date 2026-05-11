import contextlib
import pathlib
from textwrap import dedent

import pytest
from click.testing import CliRunner

from viat.cli import viat
from viat.vault import ViatVault


@pytest.fixture
def click_runner() -> CliRunner:
    return CliRunner()


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
    def test_valid(self, temp_directory: pathlib.Path, click_runner: CliRunner) -> None:
        vault = ViatVault.initialize(temp_directory)

        with vault.storage as conn, conn.get_mutator(pathlib.Path('path')) as mut:
            mut['key'] = 'value'

        with contextlib.chdir(temp_directory):
            result = click_runner.invoke(viat, ['get', 'path', 'key'])
            assert result.stdout == '"value"\n'
            assert result.stderr == ''

    def test_raw(self, temp_directory: pathlib.Path, click_runner: CliRunner) -> None:
        vault = ViatVault.initialize(temp_directory)

        with vault.storage as conn, conn.get_mutator(pathlib.Path('path')) as mut:
            mut['key'] = 'value'

        with contextlib.chdir(temp_directory):
            result = click_runner.invoke(viat, ['get', '--raw', 'path', 'key'])
            assert result.stdout == 'value\n'
            assert result.stderr == ''

    def test_path_relativization(self, temp_directory: pathlib.Path, click_runner: CliRunner) -> None:
        vault = ViatVault.initialize(temp_directory)

        with vault.storage as conn, conn.get_mutator(pathlib.Path('path')) as mut:
            mut['key'] = 'value'

        absolute_path = temp_directory.absolute().joinpath('path').as_posix()

        with contextlib.chdir(temp_directory):
            result = click_runner.invoke(viat, ['get', absolute_path, 'key'])
            assert result.stdout == '"value"\n'
            assert result.stderr == ''

    def test_missing(self, temp_directory: pathlib.Path, click_runner: CliRunner) -> None:
        ViatVault.initialize(temp_directory)

        with contextlib.chdir(temp_directory):
            result = click_runner.invoke(viat, ['get', 'path', 'key'])
            assert result.stdout == ''
            assert result.stderr == "Error: Attribute 'key' has not been set for 'path'.\n"

    def test_invalid_stored(self, temp_directory: pathlib.Path, click_runner: CliRunner) -> None:
        vault = ViatVault.initialize(temp_directory)

        with vault.storage as conn, conn.get_mutator(pathlib.Path('path')) as mut:
            mut['key'] = 'value'

        schema_path = vault.resolver.get_viat().joinpath('schema.json')
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

        with contextlib.chdir(temp_directory):
            result = click_runner.invoke(viat, ['get', 'path', 'key'])
            assert result.stdout == '"value"\n'
            assert result.stderr == "Warning: Validation error in stored data for 'path': data.key must be number.\n"


class TestGetAll:
    def test_valid(self, temp_directory: pathlib.Path, click_runner: CliRunner) -> None:
        vault = ViatVault.initialize(temp_directory)

        with vault.storage as conn, conn.get_mutator(pathlib.Path('path')) as mut:
            mut['key1'] = 'value'
            mut['key2'] = 3

        with contextlib.chdir(temp_directory):
            result = click_runner.invoke(viat, ['get-all', 'path'])
            assert result.stdout == '{"key1": "value", "key2": 3}\n'
            assert result.stderr == ''


class TestSet:
    def test_valid(self, temp_directory: pathlib.Path, click_runner: CliRunner) -> None:
        vault = ViatVault.initialize(temp_directory)

        with contextlib.chdir(temp_directory):
            result = click_runner.invoke(viat, ['set', 'path', 'key', '"value"'])
            assert result.stdout == '{"key": "value"}\n'
            assert result.stderr == ''

        with vault.storage as conn, conn.get_reader(pathlib.Path('path')) as reader:
            assert reader['key'] == 'value'

    def test_raw(self, temp_directory: pathlib.Path, click_runner: CliRunner) -> None:
        vault = ViatVault.initialize(temp_directory)

        with contextlib.chdir(temp_directory):
            result = click_runner.invoke(viat, ['set', '--raw', 'path', 'key', 'value'])
            assert result.stdout == '{"key": "value"}\n'
            assert result.stderr == ''

        with vault.storage as conn, conn.get_reader(pathlib.Path('path')) as reader:
            assert reader['key'] == 'value'

    def test_invalid_schema(self, temp_directory: pathlib.Path, click_runner: CliRunner) -> None:
        vault = ViatVault.initialize(temp_directory)

        schema_path = vault.resolver.get_viat().joinpath('schema.json')
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

        with contextlib.chdir(temp_directory):
            result = click_runner.invoke(viat, ['set', 'path', 'key', '"value"'])
            assert result.stdout == ''
            assert result.stderr == "Error: Validation error for 'path': data.key must be number.\n"
