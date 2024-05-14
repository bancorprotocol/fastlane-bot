import pytest

from fastlane_bot import Config


@pytest.fixture
def config():
    return Config.new(config=Config.CONFIG_MAINNET)
