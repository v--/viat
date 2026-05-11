import json
import pathlib
from textwrap import dedent

import pytest

from viat.exceptions import ViatStoredDataValidationWarning, ViatValidationError

from .json import JsonAttributeStorage, JsonAttributeStorageConfig


class TestJsonStorage:
    def test_basic_mutation(self, temp_directory: pathlib.Path) -> None:
        config_path = temp_directory.joinpath('config.json')
        storage = JsonAttributeStorage(JsonAttributeStorageConfig(config_path))

        with storage as conn, conn.get_mutator(pathlib.Path('table')) as mut:
            mut['key'] = 'value'

        expected_contents = json.dumps({'table': {'key': 'value'}})
        assert config_path.read_text() == expected_contents

    def test_failed_validation_for_stored_data(self, temp_directory: pathlib.Path) -> None:
        config_path = temp_directory.joinpath('config.json')
        initial_contents = json.dumps({'table': {'key': 'value'}})

        config_path.write_text(initial_contents)

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
        storage = JsonAttributeStorage(JsonAttributeStorageConfig(config_path, schema_path))

        with pytest.warns(ViatStoredDataValidationWarning):  # noqa: SIM117
            with storage as _conn:
                ...

    def test_update_failing_validation(self, temp_directory: pathlib.Path) -> None:
        config_path = temp_directory.joinpath('config.json')
        initial_contents = json.dumps({'table': {'key': 'value'}})

        config_path.write_text(initial_contents)

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
        storage = JsonAttributeStorage(JsonAttributeStorageConfig(config_path, schema_path))

        with pytest.raises(ViatValidationError):  # noqa: SIM117
            with storage as conn, conn.get_mutator(pathlib.Path('table')) as mut:
                mut['key'] = 3
