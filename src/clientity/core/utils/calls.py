# ~/clientity/src/clientity/core/utils/calls.py
from __future__ import annotations
import inspect, typing as t

from clientity.logs import log
from clientity.core.hints import Call, Callable

class __asynced:
    def check(self, call: Call) -> bool:
        return inspect.iscoroutinefunction(call)

    def wrap(self, call: Callable.Sync) -> Callable.Async:
        raise NotImplementedError

    def __call__(self, call: Call) -> Callable.Async:
        if self.check(call):
            return call
        return self.wrap(call)
asynced = __asynced()


class __sift:
    def __call__(self, *calls: Call, exhaust: bool = False) -> tuple[dict, ...]:
        raise NotImplementedError
