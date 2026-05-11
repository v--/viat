from textwrap import dedent

import tomlkit

from .toml import toml_to_json


class TestTomlToJson:
    def test_true(self) -> None:
        doc = tomlkit.parse(
            dedent("""\
                value = true
                """,
            ),
        )

        assert toml_to_json(doc['value']) is True

    def test_false(self) -> None:
        doc = tomlkit.parse(
            dedent("""\
                value = false
                """,
            ),
        )

        assert toml_to_json(doc['value']) is False

    def test_int(self) -> None:
        doc = tomlkit.parse(
            dedent("""\
                value = 3
                """,
            ),
        )

        assert isinstance(toml_to_json(doc['value']), int)

    def test_float(self) -> None:
        doc = tomlkit.parse(
            dedent("""\
                value = 3.3
                """,
            ),
        )

        assert isinstance(toml_to_json(doc['value']), float)

    def test_str(self) -> None:
        doc = tomlkit.parse(
            dedent("""\
                value = "3"
                """,
            ),
        )

        assert isinstance(toml_to_json(doc['value']), str)

    def test_table(self) -> None:
        doc = tomlkit.parse(
            dedent("""\
                [table]
                value = 3
                """,
            ),
        )

        assert toml_to_json(doc['table']) == {'value': 3}

    def test_table_array(self) -> None:
        doc = tomlkit.parse(
            dedent("""\
                [[table]]
                value = 2

                [[table]]
                value = 3
                """,
            ),
        )

        assert toml_to_json(doc['table']) == [{'value': 2}, {'value': 3}]

    def test_nested_table(self) -> None:
        doc = tomlkit.parse(
            dedent("""\
                [table.subtable]
                value = 3
                """,
            ),
        )

        assert toml_to_json(doc['table']) == {'subtable': {'value': 3}}
