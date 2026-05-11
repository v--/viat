import json
import pathlib
from textwrap import dedent

import pytest

from viat.exceptions import ViatStoredDataValidationWarning, ViatValidationError

from .json import JsonAttributeStorage, JsonAttributeStorageConfig


class TestJsonStorage:
    def test_basic_mutation(self, temp_directory: pathlib.Path) -> None:
        storage_path = temp_directory.joinpath('storage.json')
        storage = JsonAttributeStorage(JsonAttributeStorageConfig(storage_path))

        with storage as conn, conn.get_mutator('table') as mut:
            mut['key'] = 'value'

        expected_contents = json.dumps({'table': {'key': 'value'}})
        assert storage_path.read_text() == expected_contents

    def test_failed_validation_for_stored_data(self, temp_directory: pathlib.Path) -> None:
        storage_path = temp_directory.joinpath('storage.json')
        initial_contents = json.dumps({'table': {'key': 'value'}})

        storage_path.write_text(initial_contents)

        schema_path = temp_directory.joinpath('schema.json')
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
        storage = JsonAttributeStorage(JsonAttributeStorageConfig(storage_path, schema_path))

        with pytest.warns(ViatStoredDataValidationWarning):  # noqa: SIM117
            with storage as _conn:
                ...

    def test_update_failing_validation(self, temp_directory: pathlib.Path) -> None:
        storage_path = temp_directory.joinpath('storage.json')
        initial_contents = json.dumps({'table': {'key': 'value'}})

        storage_path.write_text(initial_contents)

        schema_path = temp_directory.joinpath('schema.json')
        schema = dedent("""\
            {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string"
                    }
                }
            }""",
        )

        schema_path.write_text(schema)
        storage = JsonAttributeStorage(JsonAttributeStorageConfig(storage_path, schema_path))

        with pytest.raises(ViatValidationError):  # noqa: SIM117
            with storage as conn, conn.get_mutator('table') as mut:
                mut['key'] = 3
