from unittest.mock import Mock, MagicMock

import pytest

from plugin import PluginOsu


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


@pytest.fixture
def api_mock():
    mock = Mock(spec=())
    mock.get_me = AsyncMock()
    return mock


@pytest.fixture
def local_mock():
    mock = Mock(spec=())
    return mock


@pytest.fixture
async def plugin(api_mock, mocker):
    mocker.patch('plugin.ApiClient', return_value=api_mock)
    mocker.patch('plugin.LocalClient', return_value=local_mock)
    plugin = PluginOsu(Mock(), Mock(), "handshake_token")
    plugin.push_cache = Mock(spec=())
    plugin.handshake_complete()
    yield plugin
    await plugin.shutdown()