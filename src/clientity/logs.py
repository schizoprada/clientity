from __future__ import annotations
import typing as t

from loguru import logger, Logger


class DevNull:
    def __init__(self) -> None:
       self.debug = self.__ignore
       self.info = self.__ignore
       self.warning = self.__ignore
       self.error = self.__ignore
       self.critical = self.__ignore

    def __ignore(self, *args, **kwargs) -> None: pass

devnull = DevNull()
log = logger

Log = t.Union[Logger, DevNull]
