import pathlib
from textwrap import dedent

import pytest

from viat.exceptions import (
    ViatAttributeStorageError,
    ViatMalformedStoredDataError,
    ViatStoredDataValidationWarning,
    ViatValidationError,
)

from .toml import TomlAttributeStorage, TomlAttributeStorageConfig


class TestTomlStorage:
    def test_no_storage_file(self, temp_directory: pathlib.Path) -> None:
        config_path = temp_directory.joinpath('config.toml')
        storage = TomlAttributeStorage(TomlAttributeStorageConfig(config_path))

        with storage as conn, conn.get_mutator('table') as mut:
            mut['key'] = 'value'

        expected_contents = dedent("""\
            [table]
            key = "value"
            """,
        )

        assert config_path.read_text() == expected_contents

    def test_no_storage_file_failed_creation(self, temp_directory: pathlib.Path) -> None:
        temp_directory.chmod(0o000)
        config_path = temp_directory.joinpath('config.toml')
        storage = TomlAttributeStorage(TomlAttributeStorageConfig(config_path))

        with pytest.raises(ViatAttributeStorageError):  # noqa: SIM117
            with storage as _conn:
                ...

    def test_basic_mutation(self, temp_directory: pathlib.Path) -> None:
        config_path = temp_directory.joinpath('config.toml')
        storage = TomlAttributeStorage(TomlAttributeStorageConfig(config_path))

        with storage as conn, conn.get_mutator('table') as mut:
            mut['key'] = 'value'

        expected_contents = dedent("""\
            [table]
            key = "value"
            """,
        )

        assert config_path.read_text() == expected_contents

    def test_inline_comment_preservation(self, temp_directory: pathlib.Path) -> None:
        config_path = temp_directory.joinpath('config.toml')
        initial_contents = dedent("""\
            [table]
            key = "value"  # Comment
            """,
        )

        config_path.write_text(initial_contents)
        storage = TomlAttributeStorage(TomlAttributeStorageConfig(config_path))

        with storage as conn, conn.get_mutator('table') as mut:
            mut['key'] = 'new_value'

        expected_contents = dedent("""\
            [table]
            key = "new_value"  # Comment
            """,
        )

        assert config_path.read_text() == expected_contents

    def test_automatic_table_removal(self, temp_directory: pathlib.Path) -> None:
        config_path = temp_directory.joinpath('config.toml')
        initial_contents = dedent("""\
            [table]
            key = "value"
            """,
        )

        config_path.write_text(initial_contents)
        storage = TomlAttributeStorage(TomlAttributeStorageConfig(config_path))

        with storage as conn, conn.get_mutator('table') as mut:
            del mut['key']

        assert config_path.read_text() == ''

    def test_no_key_sorting(self, temp_directory: pathlib.Path) -> None:
        config_path = temp_directory.joinpath('config.toml')
        initial_contents = dedent("""\
            [table2]
            key2 = "value2"
            key1 = "value1"

            [table1]
            key1 = "value1"
            key2 = "value2"
            """,
        )

        config_path.write_text(initial_contents)
        storage = TomlAttributeStorage(TomlAttributeStorageConfig(config_path))

        with storage as _conn:
            ...

        assert config_path.read_text() == initial_contents

    def test_inaccessible_config(self, temp_directory: pathlib.Path) -> None:
        config_path = temp_directory.joinpath('config.toml')
        config_path.touch()
        config_path.chmod(0o000)
        storage = TomlAttributeStorage(TomlAttributeStorageConfig(config_path))

        with pytest.raises(ViatAttributeStorageError):  # noqa: SIM117
            with storage as _conn:
                ...

    def test_malformed_config(self, temp_directory: pathlib.Path) -> None:
        config_path = temp_directory.joinpath('config.toml')
        config_path.write_text('gibberish')
        storage = TomlAttributeStorage(TomlAttributeStorageConfig(config_path))

        with pytest.raises(ViatMalformedStoredDataError):  # noqa: SIM117
            with storage as _conn:
                ...

    def test_failed_validation_for_stored_data(self, temp_directory: pathlib.Path) -> None:
        config_path = temp_directory.joinpath('config.toml')
        initial_contents = dedent("""\
            [table]
            key = "value"
            """,
        )

        config_path.write_text(initial_contents)

        schema_path = temp_directory.joinpath('schema.json')
        schema_path.write_text(
            dedent("""\
                {
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "number"
                        }
                    }
                }""",
            ),
        )

        storage = TomlAttributeStorage(TomlAttributeStorageConfig(config_path, schema_path))

        with pytest.warns(ViatStoredDataValidationWarning):  # noqa: SIM117
            with storage as _conn:
                ...

    def test_update_failing_validation(self, temp_directory: pathlib.Path) -> None:
        config_path = temp_directory.joinpath('config.toml')
        initial_contents = dedent("""\
            [table]
            key = "value"
            """,
        )

        config_path.write_text(initial_contents)

        schema_path = temp_directory.joinpath('schema.json')
        schema_path.write_text(
            dedent("""\
                {
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string"
                        }
                    }
                }""",
            ),
        )

        storage = TomlAttributeStorage(TomlAttributeStorageConfig(config_path, schema_path))

        with pytest.raises(ViatValidationError):  # noqa: SIM117
            with storage as conn, conn.get_mutator('table') as mut:
                mut['key'] = 3
