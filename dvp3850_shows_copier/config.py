import os
from configparser import ConfigParser, ExtendedInterpolation
from functools import lru_cache
from pathlib import Path
from typing import Optional


def get_default_config_path() -> Path:
    return Path(os.getenv('DVP3850_SHOWS_COPIER_CONFIG',
                          '~/.config/dvp3850-shows-copier/config.ini'))


@lru_cache()
def get_config(config_file: Optional[Path] = None):
    if not config_file:
        config_file = get_default_config_path()

    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read_file(config_file.expanduser().open())

    return config 
