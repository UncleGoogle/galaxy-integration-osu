from unittest.mock import Mock
import pytest

from api import ApiClient


@pytest.fixture
def store_credentials():
    return Mock()


@pytest.fixture
def auth_lost():
    return Mock()


@pytest.fixture
def api(store_credentials, auth_lost):
    return ApiClient(store_credentials, auth_lost)
