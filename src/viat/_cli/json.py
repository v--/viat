import json
from typing import override

import click

from viat.support.json import JsonObject


class JsonObjectClickType(click.ParamType):
    name = 'JSON object'

    @override
    def convert(self, value: str | JsonObject, param: click.Parameter | None, ctx: click.Context | None) -> JsonObject:
        if isinstance(value, JsonObject):
            return value

        try:
            json_value = json.loads(value)
        except json.JSONDecodeError:
            self.fail(f'Invalid JSON string {value!r}')

        if isinstance(json_value, JsonObject):
            return json_value

        self.fail(f'The JSON string {value!r} must represent an object')

