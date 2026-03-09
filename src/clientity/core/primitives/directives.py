# ~/clientity/src/clientity/core/primitives/directives.py
from __future__ import annotations
import typing as t

from clientity.logs import log

## TODO: add logging to all of these ##

class Specs:
    # update these later
    Query = t.Any
    Payload = t.Any
    Unwrap = t.Any

@t.runtime_checkable
class Directive(t.Protocol):
    def __getitem__(self, spec) -> t.Self: ...

class Query:
    """Query directive — pass kwargs as query params without a model."""
    def __init__(self) -> None: pass

    def __repr__(self) -> str: return f"Query()"

    def __getitem__(self, spec: Specs.Query) -> 'Query':
        if isinstance(spec, list):
            log.debug(f"(query.__getitem__) received list spec: {spec}")
            raise NotImplementedError
        raise ValueError(f"(Query) unsupported spec: {spec}")


class Payload:
    """Body directive — serialize kwargs with a given key."""
    key: str

    def __init__(self, key: str = "json") -> None:
        self.key = key

    def __repr__(self) -> str: return f"Payload(key={self.key!r})"

    def __getitem__(self, spec: Specs.Payload) -> 'Payload':
        if isinstance(spec, str):
            log.debug(f"(payload.__getitem__) key override: {self.key} -> {spec}")
            return Payload(key=spec)
        if isinstance(spec, (tuple, list, dict)):
            log.debug(f"(payload.__getitem__) received {type(spec)} spec: {spec}")
            raise NotImplementedError
        raise ValueError(f"(Payload) unsupported spec: {spec}")

class Unwrap:
    """Response directive — extract from response without a model."""
    key: t.Optional[str]
    pipes: list

    def __init__(
        self,
        key: t.Optional[str] = None,
        pipes: t.Optional[list] = None
        ) -> None:
        self.key = key
        self.pipes =  (pipes or [])

    @property
    def json(self) -> 'Unwrap': return Unwrap(key='json')
    @property
    def text(self) -> 'Unwrap': return Unwrap(key='text')
    @property
    def bytes(self) -> 'Unwrap': return Unwrap(key='bytes')

    def __repr__(self) -> str:  return f"Unwrap(method={self.key!r}, pipeline={self.pipes!r})"
    def __getitem__(self, spec: Specs.Unwrap) -> 'Unwrap':
        if isinstance(spec, str) or callable(spec):
            log.debug(f"(unwrap.__getitem__) received {type(spec)} spec: {spec.__name__ if callable(spec) else spec}")
            return Unwrap(key=self.key, pipes=[*self.pipes, spec])
        raise ValueError(f"(Unwrap) unsupported spec: {spec}")

    def extract(self, response) -> t.Any:
        log.debug(f"(unwrap.extract) extracting {type(response)} response")
        if not self.key:
            log.debug(f"(unwrap.extract) key not set -- returning response")
            return response # maybe None?
        raw = getattr(response, self.key)
        log.debug(f"(unwrap.extract) raw: {raw}")
        result = (raw() if callable(raw) else raw)
        for step in self.pipes:
            result = step(result) if callable(step) else result[step] # type: ignore
        log.debug(f"(unwrap.extract) result: {result}")
        return result

query = Query()
unwrap = Unwrap()
payload = Payload()
