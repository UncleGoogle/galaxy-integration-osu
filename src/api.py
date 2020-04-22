import urllib
import json
import base64
import pathlib
import typing as t

from galaxy.http import create_client_session, handle_exception
from galaxy.api.errors import AccessDenied, BackendError


class OAuthClient:
    URL = 'http://127.0.0.1:5000/'
    CLIENT_ID = 929
    START_URL = 'http://osu.ppy.sh/oauth/authorize?' + urllib.parse.urlencode({
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': URL + 'auth/osu',
        'scope': 'identify'  # 'identify+friends.read+users.read'
    })
    # http://osu.ppy.sh/oauth/authorize?response_type=code&client_id=929&redirect_uri=http://127.0.0.1:5000/auth/osu&scope=identify
    END_URL = URL + 'auth/osu/redirect'


class ApiClient:
    API_BASE_URI = 'https://osu.ppy.sh/api/v2'

    def __init__(self):
        self._session = create_client_session()
        self._access_token = None
        self._refresh_token = None
        self.user_id = 'mock id'
        self.user_name = 'mock name'

    async def _request(self, method, url, *args, **kwargs):
        with handle_exception():
            async with self._session.request(method, url, *args, **kwargs) as resp:
                return resp

    async def _api_request(self, method, part, *args, **kwargs):
        assert self._access_token
        url = self.API_BASE_URI + part
        headers = {
            "Authorization": "Bearer " + self._access_token
        }
        try:
            return await self._request(method, url, *args, headers=headers, **kwargs)
        except AccessDenied:
            await self.refresh_access_token(self._refresh_token)
            return await self._request(method, url, *args, headers=headers, **kwargs)

    def set_credentials(self, credentials: t.Dict[str, str]):
        self._refresh_token = credentials['refresh_token']
        self._access_token = credentials['access_token']
        self._expires_in = credentials['expires_in']
        self._user_id = self._decode_user_id(self._access_token)

    @staticmethod
    def _decode_user_id(token):
        data = token.split('.')[1]
        decoded = base64.b64decode(token).decode('utf-8')
        loaded = json.load(decoded)
        return loaded['sub']

    async def refresh_access_token(self, refresh_token):
        raise BackendError(f'Refreshing token currently not supported by {self.API_BASE_URI}')

    async def _get_user_name(self, user_id):
        #TODO
        res = await self._api_request('GET', '/me')  # + {mode}
        res = await self._api_request('GET', '/users/{user}/recent_activity')

    async def get_user_info(self) -> t.Tuple[str, str]:
        return self._user_id, await self._get_user_name(user_id)

