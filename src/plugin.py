import sys
import json
import webbrowser
import logging
import pathlib
from typing import List, Union

sys.path.insert(0, str(pathlib.PurePath(__file__).parent / 'modules'))

from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.types import Authentication, NextStep, Game, LicenseInfo, LicenseType, LocalGame
from galaxy.api.consts import Platform, LocalGameState

from local import LocalClient


OSU = 'osu!'

logger = logging.getLogger()

with open(pathlib.Path(__file__).parent / 'manifest.json') as f:
    __version__ = json.load(f)['version']


class PluginOsu(Plugin):
    def __init__(self, reader, writer, token):
        super().__init__(Platform.Newegg, __version__, reader, writer, token)
        self._local_client = LocalClient()

    async def authenticate(self, stored_credentials=None) -> Union[Authentication, NextStep]:
        return Authentication('osu_user', 'osu_user')
    
    async def get_owned_games(self) -> List[Game]:
        return [Game(OSU, OSU, None, LicenseInfo(LicenseType.FreeToPlay))]
    
    async def get_local_games(self) -> List[LocalGame]:
        state = LocalGameState.None_
        if self._local_client.is_installed:
            state |= LocalGameState.Installed
        if self._local_client.is_running:
            state |= LocalGameState.Running
        return [LocalGame(OSU, state)]
    
    async def install_game(self):
        webbrowser.open('https://osu.ppy.sh/home/download')
    
    async def launch_game(self):
        process = await self._local_client.launch()
        self.update_local_game_status(LocalGame(OSU, LocalGameState.Installed | LocalGameState.Running))
        await process.wait()
        self.update_local_game_status(LocalGame(OSU, LocalGameState.Installed))



def main():
    create_and_run_plugin(PluginOsu, sys.argv)

if __name__ == "__main__":
    main()