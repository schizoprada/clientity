# ~/clientity/src/clientity/core/endpoint.py
from __future__ import annotations
import typing as t

from clientity.logs import log
from clientity.core.hints import Call, Requesting, Responding
from clientity.core.primitives import (
    MethodType, Location, Locatable, Instructions, Hooks,
    GET, PUT, HEAD, POST, PATCH, DELETE, OPTIONS
)

class Endpoint:
    __copying__: set[str] = {
        'method', 'location', 'hooks',
        'querying', 'requesting', 'responding'
    }
    hooks: Hooks
    method: MethodType
    location: Location
    querying: Requesting
    requesting: Requesting
    responding: Responding

    def __init__(
        self,
        method: MethodType,
        location: Locatable = "",
        *,
        hooks: t.Optional[Hooks] = None,
        querying: Requesting = None,
        requesting: Requesting = None,
        responding: Responding = None
        ) -> None:
        self.method = method
        self.location = location if isinstance(location, Location) else Location(location)
        self.hooks = (hooks or Hooks())
        self.querying = querying
        self.requesting = requesting
        self.responding = responding


    def __copy(self, **updates) -> 'Endpoint':
        data = {
            attr: updates.get(attr, getattr(self, attr))
            for attr in self.__copying__
        }
        return Endpoint(**data)


    def at(self, path: Locatable) -> 'Endpoint':
        location = path if isinstance(path, Location) else Location(path)
        return self.__copy(location=location)

    def prehook(self, call: Call) -> 'Endpoint':
        hooks = Hooks(
            pre=[*self.hooks.pre, call],
            post=self.hooks.post.copy()
        )
        return self.__copy(hooks=hooks)

    def posthook(self, call: Call) -> 'Endpoint':
        hooks = Hooks(
            pre=self.hooks.pre.copy(),
            post=[*self.hooks.post, call]
        )
        return self.__copy(hooks=hooks)

    def queries(self, model: Requesting) -> 'Endpoint':
        return self.__copy()

    def requests(self, model: Requesting) -> 'Endpoint':
        return self.__copy()

    def responds(self, model: Responding) -> 'Endpoint':
        return self.__copy()

    def instructions(self) -> 'Instructions':
        data = {
            attr: getattr(self, attr)
            for attr in self.__copying__
        }
        return Instructions(**data)


    def __call__(self, *args, **kwargs) -> Instructions:
        """When called, return Instructions (to be executed by client)."""
        # For now just return the instructions
        # The client wrapper will handle args/kwargs at execution time
        return self.instructions()


    def __lmatmul__(self, path: Locatable) -> 'Endpoint': return self.at(path)

    def __or__(self, hook: Call) -> 'Endpoint':
        # TODO:
            # determine which hook type based on context
        raise NotImplementedError

    def __lshift__(self, model: Requesting) -> 'Endpoint':
        # TODO:
            # determine if this should go to querying or to requesting based on context
        raise NotImplementedError

    def __rshift__(self, model: Responding) -> 'Endpoint':
        return self.responds(model)


class __Factory:
    @property
    def get(self) -> Endpoint: return Endpoint(GET)
    @property
    def post(self) -> Endpoint: return Endpoint(POST)
    @property
    def put(self) -> Endpoint: return Endpoint(PUT)
    @property
    def patch(self) -> Endpoint: return Endpoint(PATCH)
    @property
    def delete(self) -> Endpoint: return Endpoint(DELETE)
    @property
    def head(self) -> Endpoint: return Endpoint(HEAD)
    @property
    def options(self) -> Endpoint: return Endpoint(OPTIONS)

endpoint = __Factory()
