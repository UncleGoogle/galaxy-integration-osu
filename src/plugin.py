import sys
import re
import json
import webbrowser
import logging
import pathlib
from typing import List, Union, Dict

sys.path.insert(0, str(pathlib.PurePath(__file__).parent / 'modules'))

from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.types import Authentication, NextStep, Game, LicenseInfo, LicenseType, LocalGame
from galaxy.api.consts import Platform, LocalGameState

from local import LocalClient
from api import ApiClient, AuthorizationClient


OSU = 'osu!'

logger = logging.getLogger()

with open(pathlib.Path(__file__).parent / 'manifest.json') as f:
    __version__ = json.load(f)['version']


class PluginOsu(Plugin):
    def __init__(self, reader, writer, token):
        super().__init__(Platform.Newegg, __version__, reader, writer, token)
        self._api = ApiClient()
        self._local = LocalClient()

    async def authenticate(self, stored_credentials=None) -> Union[Authentication, NextStep]:
        if stored_credentials is not None:
            self._api.refresh_tokens(stored_credentials['refresh_token'])
            return Authentication(self._api.user_id, self._api.user_name)
        logger.error(AuthorizationClient.GALAXY_ENTRY_POINT_PARAMS)
        return NextStep('web_session', AuthorizationClient.GALAXY_ENTRY_POINT_PARAMS)

    async def pass_login_credentials(self, step: str, credentials: Dict[str, str], cookies: List[Dict[str, str]]) \
            -> Union[NextStep, Authentication]:
        logger.debug(step)
        logger.debug(credentials)
        logger.debug(cookies)
        await self._api.load_query_credentials(credentials)
        self.store_credentials(self._api._refresh_token)
        return Authentication(self._api.user_id, self._api.user_name)

    async def get_owned_games(self) -> List[Game]:
        return [Game(OSU, OSU, None, LicenseInfo(LicenseType.FreeToPlay))]

    async def get_local_games(self) -> List[LocalGame]:
        state = LocalGameState.None_
        if self._local.is_installed:
            state |= LocalGameState.Installed
        if self._local.is_running:
            state |= LocalGameState.Running
        return [LocalGame(OSU, state)]

    async def install_game(self, game_id):
        webbrowser.open('https://osu.ppy.sh/home/download')

    async def launch_game(self, game_id):
        process = await self._local.launch()
        self.update_local_game_status(LocalGame(OSU, LocalGameState.Installed | LocalGameState.Running))
        await process.wait()
        self.update_local_game_status(LocalGame(OSU, LocalGameState.Installed))


def main():
    create_and_run_plugin(PluginOsu, sys.argv)

if __name__ == "__main__":
    main()