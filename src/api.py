import urllib
import pathlib

from galaxy.http import create_client_session, handle_exception


class ApiClient:
    CLIENT_ID = 929
    REDIRECT_URI = 'https://gog-galaxy-osu.net/redirect'
    AUTHORIZE_URI = f'http://osu.ppy.sh/oauth/authorize?' + urllib.parse.urlencode({
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'identify+friends.read+users.read'
    })
    # this works:
    # http://osu.ppy.sh/oauth/authorize?response_type=code&client_id=929&redirect_uri=https://gog-galaxy-osu.net/redirect&scope=identify+friends.read+users.read

    def __init__(self):
        self._session = create_client_session()
        self._access_token = None
        self._refresh_token = None
        self._expires_in = None
    
    async def _request(self, method, api_url, *args, **kwargs):
        base_api_url = ''
        with handle_exception():
            async with self._session.request(method, url, *args, **kwargs) as resp:
                return resp
    
    async def authorize_after_login(self, back_url):
        """TODO This code should be placed in custom server where is code is changed to refresh token
        """
        try:
            # for me
            with open(pathlib.Path(__file__).parent / '.app_credentials') as f:
                CLIENT_SECRET = f.read().strip()
        except FileNotFoundError:
            # for others
            return 'osu user', 'osu user'

        qs = back_url.split('?', 1)[-1]
        code = urllib.parse.parse_qs(qs)['code']
        params = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri': self.REDIRECT_URI
        }
        url = 'http://osu.ppy.sh/oauth/token'
        resp = await self._request('POST', url, params=params)
        self._access_token = resp['access_token']
        self._refresh_token = resp['refersh_token']
        self._expires_in = resp['expires_in']
        return resp
    
    # async def get_user_details(self):
    #     await self._request('api')
