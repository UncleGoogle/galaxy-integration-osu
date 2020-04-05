import urllib
import re
import pathlib

from galaxy.http import create_client_session, handle_exception

class AutorizationServer:
    URL = 'http://127.0.0.1:5000/'
    CLIENT_ID = 929
    AUTH_URL = URL + '/auth'
    FINAL_URL = URL + '/auth?token_type=Bearer'
    START_URL = 'http://osu.ppy.sh/oauth/authorize?' + urllib.parse.urlencode({
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': AUTH_URL,
        'scope': 'identify'  # 'identify+friends.read+users.read'
    })
    GALAXY_ENTRY_POINT_PARAMS = {
        "window_title": "Login to osu!",
        "window_width": 570,
        "window_height": 700,
        "start_uri": START_URL,
        "end_uri_regex": '^' + re.escape(FINAL_URL) + '.*'
    }
    # http://osu.ppy.sh/oauth/authorize?response_type=code&client_id=929&redirect_uri=http://127.0.0.1:5000/auth&scope=identify


class ApiClient:
    API_BASE_URI = 'https://osu.ppy.sh/api/v2'

    def __init__(self):
        self._session = create_client_session()
        self._access_token = None
        self._refresh_token = None
        self._user_id = None
        self._user_name = None
    
    @property
    def user_id(self):
        return self._user_id
    
    @property
    def user_name(self):
        return self._user_name

    async def _request(self, method, url, *args, **kwargs):
        with handle_exception():
            async with self._session.request(method, url, *args, **kwargs) as resp:
                return resp
    
    async def _api_request(self, method, part, *args, **kwargs):
        if self._access_token is None:
            raise RuntimeError('Client not authenticated!')
        url = self.API_BASE_URI + part
        return await self._request(method, url, *args, **kwargs)
    
    async def load_query_credentials(self, uri):
        qs = uri.split('?', 1)[-1]
        parsed = urllib.parse.parse_qs(qs)
        self._refresh_token = parsed['refresh_token']
        self._access_token = parsed['access_token']
        self._expires_in = parsed['expires_in']
        self._user_id = parsed['user_id']
        self._user_name = parsed['user_name']
