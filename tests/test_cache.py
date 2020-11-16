import enum
import json
from pathlib import Path

import pytest

from dvp3850_shows_copier.cache import Cache


FAKE_LIBRARY_BASE_PATH = Path('/Library')


@pytest.fixture
def fake_cache_file(shared_datadir):
    yield shared_datadir / 'cache.json'


@pytest.fixture
def fake_cache(fake_cache_file, monkeypatch):
    _fake_cache = Cache(fake_cache_file, FAKE_LIBRARY_BASE_PATH)

    import dvp3850_shows_copier.cache

    monkeypatch.setattr(dvp3850_shows_copier.cache, 'get_shows_enum', lambda base_path:
        enum.Enum('ShowsEnum', {
            'South Park': 0,
            "Rocko's Modern Life": 1
        }))

    yield _fake_cache


def test__init_empty_cache(fake_cache_file):
    fake_cache_file.unlink(missing_ok=True)

    # Init 1: no cache file exists yet.
    cache = Cache(fake_cache_file, FAKE_LIBRARY_BASE_PATH)
    assert fake_cache_file.exists()
    assert cache == {}

    # Init 2: cache file is created, but empty.
    cache = Cache(fake_cache_file, FAKE_LIBRARY_BASE_PATH)
    assert cache == {}


def test__init_existing_cache(fake_cache_file):
    cache = Cache(fake_cache_file, FAKE_LIBRARY_BASE_PATH)
    assert cache == json.load(fake_cache_file.open())


def test__set_item_raises_exc_for_unknown_show(fake_cache):
    with pytest.raises(ValueError) as err:
        fake_cache['I Do Not Exist/Season 01/S01E01.avi'] = False
    assert err.match('Unknown show')


@pytest.mark.parametrize('video_file,exp_val', [
    pytest.param('/Library/South Park/Season 01/S01E01.avi', False, id='abs-path'),
    pytest.param('South Park/Season 01/S01E01.avi', True, id='rel-path')])
def test__set_item_same_results_for_abs_or_rel_path(fake_cache, video_file, exp_val):
    fake_cache[video_file] = exp_val
    assert fake_cache._data['South Park']['Season 01']['S01E01.avi'] == exp_val


@pytest.mark.parametrize('video_file,exp_val', [
    pytest.param('/Library/South Park/Season 01/S01E01.avi', False, id='abs-path'),
    pytest.param('South Park/Season 01/S01E01.avi', True, id='rel-path')])
def test__get_item_same_results_for_abs_or_rel_path(fake_cache, video_file, exp_val):
    fake_cache._data \
        .setdefault('South Park', {}) \
        .setdefault('Season 01', {})['S01E01.avi'] = exp_val
    assert fake_cache[video_file] == exp_val


@pytest.mark.parametrize('video_file', [
    pytest.param('/Library/South Park/Season 01/S01E01.avi', id='abs-path'),
    pytest.param('South Park/Season 01/S01E01.avi', id='rel-path')])
def test__del_item_same_results_for_abs_or_rel_path(fake_cache, video_file):
    fake_cache._data \
        .setdefault('South Park', {}) \
        .setdefault('Season 01', {})['S01E01.avi'] = False
    del fake_cache[video_file]

    with pytest.raises(KeyError):
        fake_cache._data['South Park']['Season 01']['S01E01.avi']


@pytest.mark.parametrize('video_file', [
    pytest.param('/Library/South Park/Season 01/S01E01.avi', id='abs-path'),
    pytest.param('South Park/Season 01/S01E01.avi', id='rel-path')])
def test__set_compatible_same_results_for_abs_or_rel_path(fake_cache, video_file):
    fake_cache.set_compatible(video_file)
    assert fake_cache._data['South Park']['Season 01']['S01E01.avi'] == True


@pytest.mark.parametrize('video_file', [
    pytest.param('/Library/South Park/Season 01/S01E01.avi', id='abs-path'),
    pytest.param('South Park/Season 01/S01E01.avi', id='rel-path')])
def test__set_incompatible_same_results_for_abs_or_rel_path(fake_cache, video_file):
    fake_cache.set_incompatible(video_file)
    assert fake_cache._data['South Park']['Season 01']['S01E01.avi'] == False


def test__clear(fake_cache):
    assert fake_cache

    fake_cache.clear()

    assert not fake_cache
    assert not fake_cache._data


def test__write(fake_cache):
    fake_cache.cache_file.unlink()
    fake_cache._data = {}

    assert not fake_cache

    fake_cache._data \
        .setdefault('South Park', {}) \
        .setdefault('Season 01', {})['S01E01.avi'] = False

    fake_cache.write()
    assert fake_cache

    assert fake_cache == json.load(fake_cache.cache_file.open())


