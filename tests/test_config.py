from pathlib import Path

from dvp3850_shows_copier.config import get_config


def test__open

def test_config():
    config = get_config(Path('tests/data/config.ini'))

    assert config['library']['base path'] == '/media/droppie/libraries/shows'


if __name__ == '__main__':
    test_config()

