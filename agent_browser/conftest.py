import pytest
from utils.config import Config


@pytest.fixture(scope="session")
def config() -> Config:
    return Config()
