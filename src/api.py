import urllib

from galaxy.http import create_client_session, handle_exception


class ApiClient:
    CLIENT_ID = 929
    CLIENT_SECRET = '***'  # can i put it here?
    REDIRECT_URI = 'https://gog-galaxy-osu.net/redirect'
    AUTHORIZE_URI = f'http://osu.ppy.sh/oauth/authorize?' + urllib.parse.urlencode({
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'identify,friends.read,users.read'
    })
    # 'http://osu.ppy.sh/oauth/authorize?client_id=929&redirect_uri=https://gog-galaxy-osu.net/redirect&scope=identify,friends.read,users.read&state=dummy'

    def __init__(self):
        self._session = create_client_session()
        self._access_token = None
        self._refresh_token = None
        self._expires_in = None
    
    async def _request(self, method, url, *args, **kwargs):
        with handle_exception():
            async with self._session.request(method, url, *args, **kwargs) as resp:
                return resp
    
    async def authorize_after_login(self, back_url):
        qs = back_url.split('?', 1)[-1]
        code = urllib.parse.parse_qs(qs)['code']
        params = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET,
            'redirect_uri': self.REDIRECT_URI
        }
        url = 'http://osu.ppy.sh/oauth/token'
        resp = await self._request('POST', url, params=params)
        self._access_token = resp['access_token']
        self._refresh_token = resp['refersh_token']
        self._expires_in = resp['expires_in']
        return resp
