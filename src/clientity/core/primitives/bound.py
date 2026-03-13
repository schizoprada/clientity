# ~/clientity/src/clientity/core/primitives/bound.py
from __future__ import annotations
import typing as t

import typical as ty

from clientity.logs import log
from clientity.core.hints import Callable, Call, Requesting, Responding
from clientity.core.utils.calls import asynced

# pre-hinting

B = t.TypeVar('B')
R = t.TypeVar('R')

class Bound(ty.Descriptor[B, R]):
    __caller__: Callable.Async

    def __init__(self, ref: B, caller: Callable.Async) -> None:
        self.__caller__ = caller

    def __access__(self, obj: t.Any, **kwargs) -> R:
        cache = getattr(obj, '__bound__', None)
        if cache and self.__term__ in cache:
            log.debug(f"(Bound.__access__) cache hit: {self.__term__}")
            return cache[self.__term__].__caller__
        if hasattr(obj, '__wrap__'):
            log.debug(f"(Bound.__access__) lazy wrapping: {self.__term__} on {obj.__class__.__name__}")
            wrapped = obj.__wrap__(self.__ref__)
            if cache is None:
                cache = {}
                object.__setattr__(obj, '__bound__', cache)
            cache[self.__term__] = wrapped
            log.debug(f"(Bound.__access__) cached: {self.__term__}")
            return wrapped.__caller__
        log.debug(f"(Bound.__access__) fallback to direct caller: {self.__term__}")
        return self.__caller__ # type: ignore[return-value]

    async def __call__(self, *args, **kwargs) -> R:
        return await self.__caller__(*args, **kwargs)

    if t.TYPE_CHECKING:
        def __or__(self, call: Call) -> 'Bound[B, R]': ...
        def __and__(self, call: Call) -> 'Bound[B, R]': ...
        def __mod__(self, model: Requesting) -> 'Bound[B, R]': ...
        def __lshift__(self, model: Requesting) -> 'Bound[B, R]': ...
        def __matmul__(self, path: str) -> 'Bound[B, R]': ...

        @t.overload
        def __rshift__(self, model: t.Type[R]) -> 'Bound[B, R]': ...
        @t.overload
        def __rshift__(self, model: Responding) -> 'Bound[B, t.Any]': ...
        def __rshift__(self, model: t.Any) -> 'Bound[B, t.Any]': ...

'''
B = t.TypeVar("B")
class Bound(t.Generic[B]):
    __ref__: B
    __caller__: Callable.Async

    def __init__(self, ref: B, caller: Callable.Async) -> None:
        self.__ref__ = ref
        self.__caller__ = caller

    async def __call__(self, *args, **kwargs):
        return await self.__caller__(*args, **kwargs)

    if t.TYPE_CHECKING:
        def __matmul__(self, path: str) -> 'Bound[B]': ...
        def __mod__(self, model: Requesting) -> 'Bound[B]': ...
        def __lshift__(self, model: Requesting) -> 'Bound[B]': ...
        def __rshift__(self, model: Responding) -> 'Bound[B]': ...
        def __and__(self, call: Call) -> 'Bound[B]': ...
        def __or__(self, call: Call) -> 'Bound[B]': ...

'''
