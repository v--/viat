import json
import pathlib

import tomlkit
import tomlkit.exceptions

from viat.exceptions import ViatConfigError
from viat.support.json import JsonObject


def load_toml_config_file(file_path: pathlib.Path) -> JsonObject | None:
    try:
        with file_path.open() as file:
            return tomlkit.load(file).unwrap()
    except FileNotFoundError:
        return None
    except OSError as err:
        raise ViatConfigError('Could not read config file') from err
    except tomlkit.exceptions.TOMLKitError as err:
        raise ViatConfigError('Invalid TOML config file') from err


def load_json_config_file(file_path: pathlib.Path) -> JsonObject | None:
    try:
        with file_path.open() as file:
            return json.load(file)
    except FileNotFoundError:
        return None
    except OSError as err:
        raise ViatConfigError('Could not read config file') from err
    except json.decoder.JSONDecodeError as err:
        raise ViatConfigError('Invalid JSON config file') from err
