import sys
import platform
import pathlib
import asyncio

import psutil

WIN = MAC = False
if sys.platform == 'win32':
    import winreg
    WIN = True
elif sys.platform == 'darwin':
    MAC = True


class LocalClient():
    def __init__(self):
        self._exe: pathlib.Path = self._find_exe()
    
    @property
    def is_installed(self) -> bool:
        return self._exe.exists()
    
    @property
    def is_running(self):
        if self._proc is None:
            return False
        if not self._proc.is_running():
            self._proc = None
            return False
        if self._proc.status() == psutil.STATUS_ZOMBIE:
            self._proc.wait()
            return False
        return True

    def _find_exe(self) -> str:
        if not WIN:
            raise NotImplementedError('Only Windows supported for now')

        UNINSTALL_KEY = R'SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\{86ce7517-ee79-4be9-a314-128183321391}'
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, UNINSTALL_KEY) as key:
            exe = winreg.QueryValueEx(key, 'DisplayIcon')[0]
            return pathlib.Path(exe)
    
    def install(self):
        pass # TODO download exe and launch

    async def launch(self) -> asyncio.subprocess.Process:  # pylint: disable=no-member # due to pylint/issues/1469
        process = await asyncio.subprocess.create_subprocess_exec(self._exe)  #pylint: disable=no-member
        self._proc = psutil.Process(process.pid)
        return process
