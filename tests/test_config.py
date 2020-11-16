import os
from pathlib import Path

from dvp3850_shows_copier import config

import pytest


@pytest.fixture
def fake_config(shared_datadir):
    yield config.get_config(shared_datadir / 'config.ini')


def test__get_default_config_path__no_env_var(monkeypatch):
    monkeypatch.delitem(os.environ, 'DVP3850_SHOWS_COPIER_CONFIG', raising=False)

    assert config.get_default_config_path() == Path('~/.config/dvp3850-shows-copier/config.ini')


def test__get_default_config_path__with_env_var(monkeypatch, global_datadir):
    config_file = global_datadir / 'config.ini'
    monkeypatch.setitem(os.environ, 'DVP3850_SHOWS_COPIER_CONFIG', str(config_file))

    assert config.get_default_config_path() == config_file


def test__get_config_from_default_path(monkeypatch, global_datadir):
    config_file = global_datadir / 'config.ini'
    monkeypatch.setitem(os.environ, 'DVP3850_SHOWS_COPIER_CONFIG', str(config_file))
    cfg = config.get_config()

    assert cfg['general']


def test__get_config_from_provded_path(monkeypatch, global_datadir):
    config_file = global_datadir / 'config.ini'
    cfg = config.get_config(config_file)

    assert cfg['general']


def test_config(fake_config):
    assert fake_config['general']['base path'] == '/media/droppie/libraries/shows'
