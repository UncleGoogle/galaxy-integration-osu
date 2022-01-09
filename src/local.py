import abc
import sys
WIN = sys.platform == 'win32'
MAC = sys.platform == 'darwin'

import os
import logging
import pathlib
import asyncio
import typing as t
if WIN:
    import winreg

import psutil


logger = logging.getLogger(__name__)


async def run(installer_path: t.Union[str, pathlib.PurePath]) -> int:
    process = await asyncio.subprocess.create_subprocess_exec(str(installer_path))  # pylint: disable=no-member
    return await process.wait()


class InstallClient(metaclass=abc.ABCMeta):
    def __init__(self) -> None:
        self._proc: t.Optional[psutil.Process] = None
        self._exe: t.Optional[pathlib.Path] = None
        #self.check_installed_state()

    def check_installed_state(self):
        self._exe: t.Optional[pathlib.Path] = self._find_exe()

    @property
    def is_installed(self) -> bool:
        return self._exe is not None and self._exe.exists()

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

    async def launch(self) -> asyncio.subprocess.Process:  # pylint: disable=no-member # due to pylint/issues/1469
        process = await asyncio.subprocess.create_subprocess_exec(str(self._exe))  # pylint: disable=no-member
        self._proc = psutil.Process(process.pid)
        return process

    @abc.abstractmethod
    def _find_exe(self) -> t.Optional[pathlib.Path]:
        pass


class WinInstallClient(InstallClient, metaclass=abc.ABCMeta):
    EXE_NAME = "osu!.exe"

    def _find_exe(self) -> t.Optional[pathlib.Path]:
        UNINSTALL_REG = R"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        LOOKUP_REGISTRY_HIVES = [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]

        for hive in LOOKUP_REGISTRY_HIVES:
            try:
                uninstall_key_adr = UNINSTALL_REG + os.sep + self._get_uninstall_id()
                print(uninstall_key_adr)
                with winreg.OpenKey(hive, uninstall_key_adr) as uk:
                    icon_path = winreg.QueryValueEx(uk, 'DisplayIcon')[0]
                    return pathlib.Path(icon_path).parent / self.EXE_NAME
            except FileNotFoundError as e:
                print(repr(e))
                logger.debug(e)

    @abc.abstractmethod
    def _get_uninstall_id(self):
        pass


class OsuStableLocalClient(WinInstallClient):
    def _get_uninstall_id(self) -> str:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, R'Software\osu!') as key:
                uid = winreg.QueryValueEx(key, 'UninstallId')[0]
                return fR'{{{uid}}}'
        except FileNotFoundError:
            return ""


class OsuLazerLocalClient(WinInstallClient):
    def _get_uninstall_id(self) -> str:
        return 'osulazer'
