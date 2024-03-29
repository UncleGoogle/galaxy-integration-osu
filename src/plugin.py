import os
import sys
import re
import json
import webbrowser
import logging
import pathlib
from contextlib import suppress
from datetime import datetime
from urllib import parse
from typing import List, Union, Dict

sys.path.insert(0, str(pathlib.PurePath(__file__).parent / 'modules'))

import aiofiles
from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.types import Authentication, NextStep, Game, LicenseInfo, LicenseType, LocalGame, Achievement, UserInfo, UserPresence, GameTime
from galaxy.api.consts import Platform, LocalGameState, OSCompatibility, PresenceState

from local import OsuLazerLocalClient, OsuStableLocalClient, run
from api import ApiClient, OAuthClient


OSU = 'osu!'
OSU_LAZER = 'osu!(lazer)'
OSU_GAME_IDS = [OSU, OSU_LAZER]

logger = logging.getLogger()


with open(pathlib.Path(__file__).parent / 'manifest.json') as f:
    manifest = json.load(f)


class PluginOsu(Plugin):
    def __init__(self, reader, writer, token):
        super().__init__(Platform(manifest['platform']), manifest['version'], reader, writer, token)
        self._api = ApiClient(self.store_credentials, self.lost_authentication)
        self._local_clients = {
            OSU: OsuStableLocalClient(),
            OSU_LAZER: OsuLazerLocalClient()
        }

    # const game info

    async def get_owned_games(self) -> List[Game]:
        return [
            Game(id_, id_, None, LicenseInfo(LicenseType.OtherUserLicense))
            for id_ in OSU_GAME_IDS
        ]

    async def get_os_compatibility(self, game_id, context):
        return OSCompatibility.Windows  # | OSCompatibility.MacOS  # support for windows for now

    # authentication

    async def authenticate(self, stored_credentials=None) -> Union[Authentication, NextStep]:
        if stored_credentials is not None:
            return await self._auth(stored_credentials)

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
        return await self._auth(tokens)

    async def _auth(self, tokens: dict):
        self._api.set_credentials(tokens)
        return Authentication(self._api.user_id, (await self._api.get_me())['username'])

    # API features

    async def get_unlocked_achievements(self, game_id, context):
        me = await self._api.get_me()
        return [
            Achievement(
                achievement_id=medal['achievement_id'],
                unlock_time=int(datetime.fromisoformat(medal['achieved_at']).timestamp())
            )
            for medal in me.get('user_achievements', [])
        ]

    async def get_game_time(self, game_id, context):
        me = await self._api.get_me()
        seconds_played = me['statistics']['play_time']
        return GameTime(OSU, seconds_played // 60, last_played_time=None)

    async def get_friends(self):
        return [
            UserInfo(str(f['id']), f['username'], f.get('avatar_url'), 'https://osu.ppy.sh/users/' + str(f['id']))
            for f in await self._api.get_friends()
            if not f['is_bot']
        ]

    async def prepare_user_presence_context(self, user_id_list):
        return {
            str(f['id']): PresenceState.Online
            for f in await self._api.get_friends()
            if f['is_online']
        }

    async def get_user_presence(self, user_id, context):
        state = context.get(user_id, PresenceState.Offline)
        return UserPresence(state)

    # local game management

    async def get_local_games(self) -> List[LocalGame]:
        return [self._get_local_game(id_) for id_ in OSU_GAME_IDS]

    def _get_local_game(self, game_id: str) -> LocalGame:
        state = LocalGameState.None_
        if self._local_clients[game_id].is_installed:
            state |= LocalGameState.Installed
        if self._local_clients[game_id].is_running:
            state |= LocalGameState.Running
        return LocalGame(game_id, state)

    async def install_game(self, game_id):
        if game_id == OSU:
            try:
                await self._install_with_webinstaller('https://m1.ppy.sh/r/osu!install.exe')
            except Exception as e:
                logger.exception(e)
                webbrowser.open('https://osu.ppy.sh/home/download')

        if game_id == OSU_LAZER:
            # No small size installer. Let user handle by hand.
            webbrowser.open('https://github.com/ppy/osu/releases/latest/download/install.exe')
            webbrowser.open('https://github.com/ppy/osu/releases')

        self._local_clients[game_id].check_installed_state()
        if self._local_clients[game_id].is_installed:
            self.update_local_game_status(LocalGame(game_id, LocalGameState.Installed))
    
    async def _install_with_webinstaller(self, url: str):
        try:
            async with aiofiles.tempfile.NamedTemporaryFile('wb+', delete=False) as installer_bin:
                await installer_bin.write(await self._api.get_file(url))
            await run(installer_bin.name)
        finally:
            with suppress(NameError, AttributeError, FileNotFoundError):
                os.remove(installer_bin.name)

    async def uninstall_game(self, game_id: str) -> None:
        await self._local_clients[game_id].uninstall()
        if not self._local_clients[game_id].is_installed:
            self.update_local_game_status(LocalGame(game_id, LocalGameState.None_))

    async def launch_game(self, game_id):
        process = await self._local_clients[game_id].launch()
        self.update_local_game_status(LocalGame(game_id, LocalGameState.Installed | LocalGameState.Running))
        await process.wait()
        self.update_local_game_status(LocalGame(game_id, LocalGameState.Installed))


def main():
    create_and_run_plugin(PluginOsu, sys.argv)

if __name__ == "__main__":
    main()