import sys
import re
import json
import webbrowser
import logging
import pathlib
import asyncio
import tempfile
from typing import List, Union, Dict

sys.path.insert(0, str(pathlib.PurePath(__file__).parent / 'modules'))

import aiofiles
from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.types import Authentication, NextStep, Game, LicenseInfo, LicenseType, LocalGame
from galaxy.api.consts import Platform, LocalGameState

from local import LocalClient
from api import ApiClient


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
            pass  # TODO

        PARAMS = {
            "window_title": "Login to osu!",
            "window_width": 570,
            "window_height": 700,
            "start_uri": self._api.AUTHORIZE_URI,
            "end_uri_regex": '^' + re.escape(self._api.REDIRECT_URI)
        }
        return NextStep('web_session', PARAMS)

    async def pass_login_credentials(self, step: str, credentials: Dict[str, str], cookies: List[Dict[str, str]]) \
            -> Union[NextStep, Authentication]:
        logger.debug(step)
        logger.debug(credentials)
        logger.debug(cookies)
        user_id, user_name = await self._api.authorize_after_login(credentials)
        return Authentication(user_id, user_name)

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
        # if WIN:
        installer_url = 'https://m1.ppy.sh/r/osu!install.exe'
        installer_name = 'osu!install.exe'

        tmpdir = tempfile.mkdtemp()
        installer_path = pathlib.Path(tmpdir) / installer_name
        async with aiofiles.open(installer_path, mode="wb") as installer_bin:
            await installer_bin.write(await self._api.get_file(installer_url))
        await asyncio.subprocess.run(installer_path)
        self.update_local_game_status(LocalGame(OSU, LocalGameState.Installed))
        tmpdir.cleanup()

    async def launch_game(self, game_id):
        process = await self._local.launch()
        self.update_local_game_status(LocalGame(OSU, LocalGameState.Installed | LocalGameState.Running))
        await process.wait()
        self.update_local_game_status(LocalGame(OSU, LocalGameState.Installed))


def main():
    create_and_run_plugin(PluginOsu, sys.argv)

if __name__ == "__main__":
    main()