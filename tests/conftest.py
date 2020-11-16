from pathlib import Path

import pytest


@pytest.fixture
def global_datadir():
    yield Path(__file__).parent / 'data'