import os
from configparser import ConfigParser, ExtendedInterpolation
from functools import lru_cache
from pathlib import Path
from typing import Optional


class Converters:
    @staticmethod
    def opts(val):
        opts_list = val.strip().splitlines()
        return ' '.join(opts_list)

    def path(val):
        return Path(val).expanduser()


def get_default_config_path() -> Path:
    return Path(os.getenv('DVP3850_SHOWS_COPIER_CONFIG',
                          '~/.config/dvp3850-shows-copier/config.ini'))


@lru_cache()
def get_config(config_file: Optional[Path] = None):
    if not config_file:
        config_file = get_default_config_path()

    config = ConfigParser(interpolation=ExtendedInterpolation(),
                          converters={'opts': Converters.opts,
                                      'path': Converters.path})
    config.read_file(config_file.expanduser().open())

    return config 
