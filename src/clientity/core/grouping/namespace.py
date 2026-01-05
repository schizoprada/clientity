# ~/clientity/src/clientity/core/grouping/namespace.py
from __future__ import annotations
import typing as t

from clientity.logs import log
from clientity.core.hints import Responded
from clientity.core.utils import (
    bound, synced, domain,
    sift, dictate, embody
)
from clientity.core.endpoint import Endpoint
from clientity.core.adapters import Adapter, adapt
from clientity.core.protocols import (
    Located, Interface, Interfacing
)
from clientity.core.primitives import (
    Bound, Instructions,
    URL, Location, Locatable
)
from clientity.core.grouping.base import Grouping, WrappedEndpoint
from clientity.core.grouping.resource import Resource


class Namespace(Grouping):
    base: str
    adapter: t.Optional[Adapter] = None
    interface: t.Optional[Interface] = None

    def __init__(
        self,
        base: str = "",
        name: str = "",
        interface: t.Optional[Interfacing] = None
        ) -> None:
        self.base = base.rstrip("/")
        self.name = name if name else (domain(self.base) if self.base else "")
        if interface is not None:
            self.interface = interface if( not callable(interface)) else (synced(interface)())
            self.adapter = adapt(self.interface)


    @property
    def independent(self) -> bool:
        return (self.interface is not None)

    async def __x(self, instructions: Instructions, *args, **kwargs) -> Responded:
        if not self.adapter:
            raise RuntimeError(f"(Namespace[{self.name}]) no adapter to execute request")

        pdata, qdata, bdata = sift.instructions(*args, provided=instructions, **kwargs)
        url = URL(self.base, instructions.location).resolve(**pdata)
        query, body = None, None

        if (qdata and instructions.querying):
            query = dictate(instructions.querying(**qdata))

        if (bdata and instructions.requesting):
            body = embody(instructions.requesting(**bdata))

        request = self.adapter.build(url=url, method=instructions.method, params=query, body=body)
        for hook in instructions.hooks.before:
            request = await hook(request)

        response = await self.adapter.send(request)
        for hook in instructions.hooks.after:
            response = await hook(response)

        if instructions.responding:
            if hasattr(instructions.responding, '__respond__'):
                return instructions.responding.__respond__(response)

        return response

    def __wrap__(self, endpoint: Endpoint) -> WrappedEndpoint:
        if self.adapter is None:
            log.debug(f"(Namespace[{self.name}]) passing through endpoint: {endpoint.location}")
            return endpoint
        log.debug(f"(Namespace[{self.name}]) wrapping endpoint @ {endpoint.location}")
        ns = self

        async def wrapper(*args, **kwargs) -> Responded:
            return await ns.__x(endpoint.instructions(), *args, **kwargs)

        return bound(endpoint, wrapper)

    def __nest__(self, child: Located) -> Resource:
        if not isinstance(child, Resource):
            raise TypeError(f"(Namespace[{self.name}]) cannot nest: {child.__class__.__name__}")
        log.debug(f"(Namespace[{self.name}]) nesting resource: {child.name})")
        nested = Resource(child.location)
        for name, endpoint in child.endpoints():
            setattr(nested, name, endpoint)
        return nested

    def __matmul__(self, base: str) -> 'Namespace':
        log.debug(f"(Namespace) basing @ {base}")
        return Namespace(base, self.name, self.interface)
