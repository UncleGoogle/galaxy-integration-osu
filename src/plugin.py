import sys
import re
import json
import webbrowser
import logging
import pathlib
from datetime import datetime
from urllib import parse
from typing import List, Union, Dict

sys.path.insert(0, str(pathlib.PurePath(__file__).parent / 'modules'))

from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.types import Authentication, NextStep, Game, LicenseInfo, LicenseType, LocalGame, Achievement
from galaxy.api.consts import Platform, LocalGameState, OSCompatibility

from local import LocalClient
from api import ApiClient, OAuthClient


OSU = 'osu!'

logger = logging.getLogger()

with open(pathlib.Path(__file__).parent / 'manifest.json') as f:
    __version__ = json.load(f)['version']


class PluginOsu(Plugin):
    def __init__(self, reader, writer, token):
        super().__init__(Platform.Newegg, __version__, reader, writer, token)
        self._api = ApiClient(self.store_credentials, self.lost_authentication)
        self._local = LocalClient()

    async def authenticate(self, stored_credentials=None) -> Union[Authentication, NextStep]:
        if stored_credentials is not None:
            self._api.set_credentials(stored_credentials)
            return Authentication(self._api.user_id, (await self._api.get_me())['username'])

        return NextStep('web_session', {
            "window_title": "Login to osu!",
            "window_width": 570,
            "window_height": 700,
            "start_uri": OAuthClient.START_URL,
            "end_uri_regex": '^' + re.escape(OAuthClient.END_URL) + r'\?.*token_type=Bearer.*'
        })

    async def pass_login_credentials(self, step: str, credentials: Dict[str, str], cookies: List[Dict[str, str]]) \
            -> Union[NextStep, Authentication]:
        query_string = parse.urlsplit(credentials['end_uri']).query
        tokens = dict(parse.parse_qsl(query_string))
        self._api.set_credentials(tokens)
        return Authentication(self._api.user_id, (await self._api.get_me())['username'])

    async def get_owned_games(self) -> List[Game]:
        return [Game(OSU, OSU, None, LicenseInfo(LicenseType.OtherUserLicense))]

    async def get_os_compatibility(self, game_id, context):
        return OSCompatibility.Windows | OSCompatibility.MacOS

    async def get_local_games(self) -> List[LocalGame]:
        state = LocalGameState.None_
        if self._local.is_installed:
            state |= LocalGameState.Installed
        if self._local.is_running:
            state |= LocalGameState.Running
        return [LocalGame(OSU, state)]

    async def install_game(self, game_id):
        await self._api._refresh_access_token()
        webbrowser.open('https://osu.ppy.sh/home/download')

    async def launch_game(self, game_id):
        process = await self._local.launch()
        self.update_local_game_status(LocalGame(OSU, LocalGameState.Installed | LocalGameState.Running))
        await process.wait()
        self.update_local_game_status(LocalGame(OSU, LocalGameState.Installed))

    async def get_unlocked_achievements(self, game_id, context):
        me = await self._api.get_me()
        return [
            Achievement(
                achievement_id=medal['achievement_id'],
                unlock_time=int(datetime.fromisoformat(medal['achieved_at']).timestamp())
            )
            for medal in me.get('user_achievements', [])
        ]


def main():
    create_and_run_plugin(PluginOsu, sys.argv)

if __name__ == "__main__":
    main()