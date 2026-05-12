import json
import pathlib
import tomllib
from typing import overload

from viat.exceptions import ViatConfigError
from viat.support.json import Json, JsonObject


class ConfigLoader:
    payload: JsonObject

    @staticmethod
    def try_load_toml_file(file_path: pathlib.Path) -> 'ConfigLoader | None':
        try:
            with file_path.open('rb') as file:
                contents = tomllib.load(file)
        except FileNotFoundError:
            return None
        except OSError as err:
            raise ViatConfigError('Could not read config file') from err
        except tomllib.TOMLDecodeError as err:
            raise ViatConfigError('Invalid TOML config file') from err

        return ConfigLoader(contents)

    @staticmethod
    def try_load_json_file(file_path: pathlib.Path) -> 'ConfigLoader | None':
        try:
            with file_path.open() as file:
                contents = json.load(file)
        except FileNotFoundError:
            return None
        except OSError as err:
            raise ViatConfigError('Could not read config file') from err
        except json.decoder.JSONDecodeError as err:
            raise ViatConfigError('Invalid JSON config file') from err

        if not isinstance(contents, JsonObject):
            raise ViatConfigError('The configuration must be a JSON object')

        return ConfigLoader(contents)

    def __init__(self, payload: JsonObject) -> None:
        self.payload = payload

    def get_nested(self, *segments: str) -> Json:
        config = self.payload

        if len(segments) == 0:
            return config

        for i, segment in enumerate(segments[:-1]):
            current = config.get(segment)

            match current:
                case None:
                    return current

                case JsonObject():
                    config = current

                case _:
                    raise ViatConfigError(f'The {".".join(segments[:i + 1])} configuration must be a table')

        return config.get(segments[-1])

    @overload
    def get_bool(self, *segments: str, default: bool) -> bool: ...
    @overload
    def get_bool(self, *segments: str, default: bool | None = None) -> bool | None: ...
    def get_bool(self, *segments: str, default: bool | None = None) -> bool | None:
        match value := self.get_nested(*segments):
            case None:
                return default

            case bool():
                return value

            case _:
                raise ViatConfigError(f'The {".".join(segments)} option must be a boolean')

    @overload
    def get_int(self, *segments: str, default: int) -> int: ...
    @overload
    def get_int(self, *segments: str, default: int | None = None) -> int | None: ...
    def get_int(self, *segments: str, default: int | None = None) -> int | None:
        match value := self.get_nested(*segments):
            case None:
                return default

            case int():
                return value

            case _:
                raise ViatConfigError(f'The {".".join(segments)} option must be an integer')

    @overload
    def get_str(self, *segments: str, default: str) -> str: ...
    @overload
    def get_str(self, *segments: str, default: str | None = None) -> str | None: ...
    def get_str(self, *segments: str, default: str | None = None) -> str | None:
        match value := self.get_nested(*segments):
            case None:
                return default

            case str() | None:
                return value

            case _:
                raise ViatConfigError(f'The {".".join(segments)} option must be an string')

    @overload
    def get_path(self, *segments: str, root: pathlib.Path, default: pathlib.Path) -> pathlib.Path: ...
    @overload
    def get_path(self, *segments: str, root: pathlib.Path, default: pathlib.Path | None = None) -> pathlib.Path | None: ...
    def get_path(self, *segments: str, root: pathlib.Path, default: pathlib.Path | None = None) -> pathlib.Path | None:
        match value := self.get_nested(*segments):
            case None:
                return default

            case str():
                return root / value

            case _:
                raise ViatConfigError(f'The {".".join(segments)} option must be a path')
