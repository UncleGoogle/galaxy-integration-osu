import logging
import urllib
import json
import base64
import pathlib
import typing as t

from galaxy.http import create_client_session, handle_exception
from galaxy.api.errors import AccessDenied, AuthenticationRequired


logger = logging.getLogger(__name__)


class OAuthClient:
    URL = 'https://unclegoogle.pythonanywhere.com/'
    CLIENT_ID = 929
    START_URL = 'http://osu.ppy.sh/oauth/authorize?' + urllib.parse.urlencode({
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': URL + 'auth/osu',
        'scope': 'identify'  # 'identify+friends.read+users.read'
    })
    END_URL = URL + 'auth/osu/redirect'


class ApiClient:
    API_BASE_URI = 'https://osu.ppy.sh/api/v2'

    def __init__(self, store_credentials: t.Callable, auth_lost: t.Callable):
        self._session = create_client_session()
        self._access_token = None
        self._refresh_token = None
        self._user_id = None
        self._store_credentials = store_credentials
        self._auth_lost = auth_lost

    @property
    def user_id(self):
        return self._user_id

    @staticmethod
    def _user_id_from_jwt(token: str):
        data = token.split('.')[1] + '=='
        decoded = base64.b64decode(data).decode('utf-8')
        loaded = json.loads(decoded)
        return loaded['sub']

    def set_credentials(self, credentials: t.Dict[str, str]):
        self._refresh_token = credentials['refresh_token']
        self._access_token = credentials['access_token']
        self._expires_in = credentials['expires_in']
        self._user_id = self._user_id_from_jwt(self._access_token)
        self._store_credentials(credentials)

    async def _request(self, method, url, *args, **kwargs):
        with handle_exception():
            async with self._session.request(method, url, *args, **kwargs) as resp:
                return resp

    async def _refresh_access_token(self):
        params = {
            'grant_type': 'refresh_token',
            'refresh_token': self._refresh_token
        }
        response = await self._request('POST', json=params)
        data = await response.json()
        self.set_credentials(data)

    async def _api_request(self, method, part, *args, **kwargs):
        assert self._access_token
        url = self.API_BASE_URI + part
        headers = {
            "Authorization": "Bearer " + self._access_token
        }
        try:
            return await self._request(method, url, *args, headers=headers, **kwargs)
        except (AuthenticationRequired, AccessDenied):
            try:
                await self._refresh_access_token()
            except Exception as e:
                logger.error('Cannot refresh access token: %s', repr(e))
                self._auth_lost()
            else:
                try:
                    return await self._request(method, url, *args, headers=headers, **kwargs)
                except (AuthenticationRequired, AccessDenied) as e:
                    logger.error('Cannot access %s: %s', url, repr(e))
                    self._auth_lost()

    async def get_user_name(self):
        #TODO
        # res = await self._api_request('GET', '/me')  # + {mode}
        # res = await self._api_request('GET', '/users/{user}/recent_activity')
        return 'Osu user'
