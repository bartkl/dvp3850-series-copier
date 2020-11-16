import os
from configparser import ConfigParser, ExtendedInterpolation
from functools import lru_cache
from pathlib import Path
from typing import Optional, Union


DEFAULT_CONFIG_FILE = Path(os.getenv('DVP3850_SHOWS_COPIER_CONFIG',
    '~/.config/dvp3850-shows-copier/config.ini'))


class Converters:
    @staticmethod
    def abspath(val):
        return Path(val).expanduser().absolute()


@lru_cache()
def get_config(config_file: Optional[Path] = DEFAULT_CONFIG_FILE):
    config = ConfigParser(
        interpolation=ExtendedInterpolation(),
        converters={'abspath': Converters.abspath})

    config.read_file(config_file.expanduser().open())

    return config 
