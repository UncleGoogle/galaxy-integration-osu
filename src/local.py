import sys
WIN = sys.platform == 'win32'
MAC = sys.platform == 'darwin'

import logging
import pathlib
import asyncio
import typing as t
if WIN:
    import winreg

import psutil


logger = logging.getLogger(__name__)


class LocalClient():
    def __init__(self):
        self._exe: t.Optional[pathlib.Path] = self._find_exe()
        self._proc: t.Optional[psutil.Process] = None

    @property
    def is_installed(self) -> bool:
        return self._exe and self._exe.exists()

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

    def _find_exe(self) -> t.Optional[str]:
        if not WIN:
            raise NotImplementedError('Only Windows supported for now')

        UNINSTALL_REG = R'SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall'
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, R'Software\osu!') as key:
                uninstall_id = winreg.QueryValueEx(key, 'UninstallId')[0]
                uninstall_key = UNINSTALL_REG + fR'\{{{uninstall_id}}}'
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, uninstall_key) as key:
                exe = winreg.QueryValueEx(key, 'DisplayIcon')[0]
                return pathlib.Path(exe)
        except FileNotFoundError:
            return None

    async def install(self, installer_path) -> int:
        process = await asyncio.subprocess.create_subprocess_exec(str(installer_path))  # pylint: disable=no-member
        returncode = await process.wait()
        self._find_exe()
        return returncode

    async def launch(self) -> asyncio.subprocess.Process:  # pylint: disable=no-member # due to pylint/issues/1469
        process = await asyncio.subprocess.create_subprocess_exec(str(self._exe))  # pylint: disable=no-member
        self._proc = psutil.Process(process.pid)
        return process
