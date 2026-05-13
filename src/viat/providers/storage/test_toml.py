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
        storage_path = temp_directory.joinpath('storage.toml')
        storage = TomlAttributeStorage(TomlAttributeStorageConfig(storage_path))

        with storage as conn, conn.get_mutator('table') as mut:
            mut['key'] = 'value'

        expected_contents = dedent("""\
            [table]
            key = "value"
            """,
        )

        assert storage_path.read_text() == expected_contents

    def test_no_storage_file_failed_creation(self, temp_directory: pathlib.Path) -> None:
        temp_directory.chmod(0o000)
        storage_path = temp_directory.joinpath('storage.toml')
        storage = TomlAttributeStorage(TomlAttributeStorageConfig(storage_path))

        with pytest.raises(ViatAttributeStorageError):  # noqa: SIM117
            with storage as _conn:
                ...

    def test_basic_mutation(self, temp_directory: pathlib.Path) -> None:
        storage_path = temp_directory.joinpath('storage.toml')
        storage = TomlAttributeStorage(TomlAttributeStorageConfig(storage_path))

        with storage as conn, conn.get_mutator('table') as mut:
            mut['key'] = 'value'

        expected_contents = dedent("""\
            [table]
            key = "value"
            """,
        )

        assert storage_path.read_text() == expected_contents

    # The initial version of this tool used tomlkit, which has the ability to preserve comments.
    # Unfortunately, it was very slow, and so we replaced it with tomllib + tomli_w.
    # This test just confirms that TOML comments get removed, as a way to highlight that this is expected.
    def test_inline_comment_removal(self, temp_directory: pathlib.Path) -> None:
        storage_path = temp_directory.joinpath('storage.toml')
        initial_contents = dedent("""\
            [table]
            key = "value"  # Comment
            """,
        )

        storage_path.write_text(initial_contents)
        storage = TomlAttributeStorage(TomlAttributeStorageConfig(storage_path))

        with storage as conn, conn.get_mutator('table') as mut:
            mut['key'] = 'new_value'

        expected_contents = dedent("""\
            [table]
            key = "new_value"
            """,
        )

        assert storage_path.read_text() == expected_contents

    def test_automatic_table_removal(self, temp_directory: pathlib.Path) -> None:
        storage_path = temp_directory.joinpath('storage.toml')
        initial_contents = dedent("""\
            [table]
            key = "value"
            """,
        )

        storage_path.write_text(initial_contents)
        storage = TomlAttributeStorage(TomlAttributeStorageConfig(storage_path))

        with storage as conn, conn.get_mutator('table') as mut:
            del mut['key']

        assert storage_path.read_text() == ''

    def test_no_key_sorting(self, temp_directory: pathlib.Path) -> None:
        storage_path = temp_directory.joinpath('storage.toml')
        initial_contents = dedent("""\
            [table2]
            key2 = "value2"
            key1 = "value1"

            [table1]
            key1 = "value1"
            key2 = "value2"
            """,
        )

        storage_path.write_text(initial_contents)
        storage = TomlAttributeStorage(TomlAttributeStorageConfig(storage_path))

        with storage as _conn:
            ...

        assert storage_path.read_text() == initial_contents

    def test_not_saving_without_mutation(self, temp_directory: pathlib.Path) -> None:
        storage_path = temp_directory.joinpath('storage.toml')
        storage_path.touch()
        expected_mod_time = storage_path.stat().st_mtime
        storage = TomlAttributeStorage(TomlAttributeStorageConfig(storage_path))

        with storage as conn, conn.get_reader('test') as _reader:
            ...

        actual_mod_time = storage_path.stat().st_mtime
        assert actual_mod_time == expected_mod_time

    def test_inaccessible_config(self, temp_directory: pathlib.Path) -> None:
        storage_path = temp_directory.joinpath('storage.toml')
        storage_path.touch()
        storage_path.chmod(0o000)
        storage = TomlAttributeStorage(TomlAttributeStorageConfig(storage_path))

        with pytest.raises(ViatAttributeStorageError):  # noqa: SIM117
            with storage as _conn:
                ...

    def test_malformed_config(self, temp_directory: pathlib.Path) -> None:
        storage_path = temp_directory.joinpath('storage.toml')
        storage_path.write_text('gibberish')
        storage = TomlAttributeStorage(TomlAttributeStorageConfig(storage_path))

        with pytest.raises(ViatMalformedStoredDataError):  # noqa: SIM117
            with storage as _conn:
                ...

    def test_failed_validation_for_stored_data(self, temp_directory: pathlib.Path) -> None:
        storage_path = temp_directory.joinpath('storage.toml')
        initial_contents = dedent("""\
            [table]
            key = "value"
            """,
        )

        storage_path.write_text(initial_contents)

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

        storage = TomlAttributeStorage(TomlAttributeStorageConfig(storage_path, schema_path))

        with pytest.warns(ViatStoredDataValidationWarning):  # noqa: SIM117
            with storage as _conn:
                ...

    def test_update_failing_validation(self, temp_directory: pathlib.Path) -> None:
        storage_path = temp_directory.joinpath('storage.toml')
        initial_contents = dedent("""\
            [table]
            key = "value"
            """,
        )

        storage_path.write_text(initial_contents)
        expected_mod_time = storage_path.stat().st_mtime

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

        storage = TomlAttributeStorage(TomlAttributeStorageConfig(storage_path, schema_path))

        with pytest.raises(ViatValidationError):  # noqa: SIM117
            with storage as conn, conn.get_mutator('table') as mut:
                mut['key'] = 3

        actual_mod_time = storage_path.stat().st_mtime
        assert actual_mod_time == expected_mod_time

    def test_update_with_null(self, temp_directory: pathlib.Path) -> None:
        storage_path = temp_directory.joinpath('storage.toml')
        storage_path.touch()
        storage = TomlAttributeStorage(TomlAttributeStorageConfig(storage_path))

        with pytest.raises(ViatAttributeStorageError):  # noqa: SIM117
            with storage as conn, conn.get_mutator('table') as mut:
                mut['key'] = None
