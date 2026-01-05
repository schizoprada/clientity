# ~/clientity/src/clientity/core/primitives/bound.py
from __future__ import annotations
import typing as t

from clientity.core.hints import Callable, ResponseObject
from clientity.core.utils import asynced

B = t.TypeVar("B")
class Bound(t.Generic[B]):
    __ref__: B
    __caller__: Callable.Async

    def __init__(self, ref: B, caller: Callable.Async) -> None:
        self.__ref__ = ref
        self.__caller__ = caller

    async def __call__(self, *args, **kwargs):
        return await self.__caller__(*args, **kwargs)
