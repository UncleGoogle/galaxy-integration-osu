import urllib
import pathlib

from galaxy.http import create_client_session, handle_exception
from galaxy.api.errors import AccessDenied


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

    @property
    def refresh_token(self):
        return self._refresh_token

    async def _request(self, method, url, *args, **kwargs):
        with handle_exception():
            async with self._session.request(method, url, *args, **kwargs) as resp:
                return resp

    async def _api_request(self, method, part, *args, **kwargs):
        if self._access_token is None:
            raise RuntimeError('Client not authenticated!')

        url = self.API_BASE_URI + part
        try:
            return await self._request(method, url, *args, **kwargs)
        except AccessDenied:
            self.authorize(self._refresh_token)
            return await self._request(method, url, *args, **kwargs)

    def load_query_credentials(self, uri):
        qs = uri.split('?', 1)[-1]
        parsed = urllib.parse.parse_qs(qs)
        self._refresh_token = parsed['refresh_token']
        self._access_token = parsed['access_token']
        self._expires_in = parsed['expires_in']

    async def authorize(self, refresh_token):
        params = {
            ''
        }

    async def get_user_info(self):
        pass

