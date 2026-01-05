# ~/clientity/src/clientity/core/client.py
from __future__ import annotations
import typing as t

from clientity.logs import log
from clientity.core.hints import ResponseObject, Responded
from clientity.core.utils import (
    sift, embody, domain,
    synced, dictate, bound
)
from clientity.core.endpoint import Endpoint
from clientity.core.protocols import (
    Interface,
    Interfacing
)
from clientity.core.primitives import (
    URL, Location, Locatable,
    Instructions, Bound
)
from clientity.core.adapters import adapt, Adapter

class Client:
    base: str
    interface: Interface

    def __init__(
        self,
        interface: Interfacing,
        base: str = "",
        name: str = ""
        ) -> None:
        self.name = (name or domain(base))
        self.base = base.rstrip("/")
        self.interface = interface if (not callable(interface)) else (synced(interface)())
        self.adapter: Adapter = adapt(self.interface)

    async def __x(
        self,
        instructions: Instructions,
        exhaust: bool = False,
        *args, **kwargs
        ) -> Responded:
        pdata, qdata, bdata = sift.instructions(*args, provided=instructions, exhaust=exhaust, **kwargs)

        url = URL(self.base, instructions.location).resolve(**pdata)
        query, body = None, None

        if (qdata and instructions.querying):
            query = dictate(instructions.querying(**qdata))

        if (bdata and instructions.requesting):
            body = embody(instructions.requesting(**bdata))

        # TODO: adapter for request objects
        request = self.adapter.build(
            url=url, method=instructions.method,
            params=query, body=body
        )
        for hook in instructions.hooks.before:
            request = await hook(request)

        # TODO: interface send()
        response = await self.adapter.send(request)
        for hook in instructions.hooks.after:
            response = await hook(response)

        if instructions.responding:
            if hasattr(instructions.responding, '__respond__'):
                return instructions.responding.__respond__(response)

        return response



    def __wrap(self, endpoint: Endpoint, exhaust: bool = False,) -> Bound[Endpoint]:
        async def wrapper(*args, **kwargs) -> Responded:
            return await self.__x(endpoint.instructions(), exhaust, *args, **kwargs)
        return bound(endpoint, wrapper)

    def __setattr__(self, name: str, value: t.Any) -> None:
        attr = value
        if isinstance(value, Endpoint):
            attr = self.__wrap(value)
        super().__setattr__(name, attr)




def client(interface: Interface) -> Client:
    return Client(interface)
