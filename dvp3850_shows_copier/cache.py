import json
from functools import lru_cache
from collections.abc import MutableMapping
from contextlib import contextmanager
from pathlib import Path
from typing import Union, Optional, TextIO, Dict

JsonData = Union[Dict, str]


@lru_cache()
def get_shows_enum(base_path: Path):
    return enum.Enum('ShowsEnum',
        {show.name: i for i, show in enumerate(base_path.iterdir())})


class Cache(MutableMapping):

    def __init__(self,
                 cache_file: Path,
		 base_path: Path,
                 data: JsonData = '{}'):
        self._data = {}
        self.cache_file = cache_file
	self.base_path = base_path

        if not self.cache_file.exists():
            self.cache_file.touch()
        else:
            with self._open() as cache:
                self._data.update(json.load(cache))

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def __eq__(self, other):
        return self.items() == other.items()

    def __delitem__(self, video_file):
        show, season, episode = self._key_from_path(video_file)
        del self._data \
            .get(show) \
            .get(season) \
            [episode]

    def __getitem__(self, video_file):
        show, season, episode = self._key_from_path(video_file)
        return self._data \
            .get(show) \
            .get(season) \
            [episode]

    def __setitem__(self, video_file: Union[Path, str], compat_val: int):
        show, season, episode = self._key_from_path(video_file)
        self._data \
            .setdefault(show, {}) \
            .setdefault(season, {}) \
            [episode] = compat_val

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return repr(self._data)

    def clear(self):
        self._data = {}


    def _key_from_path(self, video_file: Union[Path, str]):
        video_file = Path(video_file)

        if self.base_path in video_file.parents:
            video_file = video_file.relative_to(self.base_path)

        show, season, episode = video_file.parts

        if show not in get_shows_enum(self.base_path)._member_names_:
            raise ValueError(f'Unknown show "{show}".')

        return show, season, episode
    
    @contextmanager
    def _open(self, mode: str = 'r') -> TextIO:
        cache = open(self.cache_file, mode)
        yield cache
        cache.close()

    def read(self):
        with self._open() as cache:
            self._data = json.load(cache)

    def set_compatible(self, video_file: Union[Path, str]):
        self[video_file] = True

    def set_incompatible(self, video_file: Union[Path, str]):
        self[video_file] = False

    def write(self):
        with self._open(mode='w') as cache:
            cache.write(json.dumps(self._data, sort_keys=True, indent=4))

