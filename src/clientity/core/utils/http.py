# ~/clientity/src/clientity/core/utils/http.py
from __future__ import annotations
import typing as t

from urllib.parse import urlparse

from clientity.exc import ModelingError, ResponseError
from clientity.logs import log
from clientity.core.hints import Requested, Embodied, Responded
from clientity.core.protocols import Requestable
from clientity.core.primitives import (
    URL, Directive, Specs,
    Query, Payload, Unwrap
)
from clientity.core.utils.calls import sift
from clientity.core.utils.models import dictate, respond
if t.TYPE_CHECKING:
    from clientity.core.adapters import Adapter
    from clientity.core.primitives import Instructions

def embody(obj: Requested) -> t.Optional[Embodied]:
    if obj is None: return None

    if isinstance(obj, Requestable):
        key = getattr(obj, "RequestKey", "json")
        return key, obj.__request__()

    if isinstance(obj, dict):
        return "json", obj

    if isinstance(obj, bytes):
        return "data", obj

    # TODO: handle known libraries e.g. dataclasses, pydantic

    return "json", dictate(obj)


def domain(url: str) -> str:
    parsed = urlparse(url)
    splits = parsed.path.split('/')[0]
    value = (parsed.netloc or splits)
    log.debug(f"(domain) parsed {url} -> {value}")
    return value

class __execute:
    def __query(
        self,
        querying: t.Any,
        qdata: dict,
        claimed: set[str],
        **kwargs
        ) -> t.Optional[dict]:
        if isinstance(querying, Query):
            # v1: no field list, nothing to claim
            # future: Query with field list claims here
            log.debug(f"(http.execute.__query) directive active -- no fields to claim")
            return None
        if not qdata: return None

        log.debug(f"(http.execute.__query) preparing: {qdata}")
        query = qdata if not querying else dictate(querying(**qdata))
        claimed |= set(qdata.keys())
        log.debug(f"(http.execute.__query) prepared: {query}")
        return query

    def __body(
        self,
        requesting: t.Any,
        bdata: dict,
        claimed: set[str],
        **kwargs
        ) -> t.Optional[Embodied]:
        if isinstance(requesting, Payload):
            leftover = {k: v for k, v in kwargs.items() if k not in claimed}
            if not leftover: return None
            log.debug(f"(http.execute.__body) payload [{requesting.key}]: {leftover}")
            return (requesting.key, leftover)
        if not bdata: return None
        log.debug(f"(http.execute.__body) preparing: {bdata}")
        body = embody(bdata) if not requesting else embody(requesting(**bdata))
        log.debug(f"(http.execute.__body) prepared: {body}")
        return body

    def __response(
        self,
        responding: t.Any,
        response: t.Any
        ) -> Responded:
        if isinstance(responding, Unwrap):
            log.debug(f"(http.execute.__response) unwrapping: {responding}")
            return responding.extract(response)
        if responding:
            log.debug(f"(http.execute.__response) modeling: {responding.__name__}")
            try:
                return respond(responding, response)
            except (ModelingError, ResponseError) as e:
                log.error(f"(http.execute.__response) model error (returning raw): {e!r}")
        return response

    async def __call__(
        self,
        base: str,
        adapter: 'Adapter',
        instructions: 'Instructions',
        exhaust: bool = False,
        *args, **kwargs
        ) -> Responded:
        pdata, qdata, bdata = sift.instructions(*args, provided=instructions, exhaust=exhaust, **kwargs)
        url = URL(base, instructions.location).resolve(**pdata)
        claimed = set(pdata.keys())

        query = self.__query(instructions.querying, qdata, claimed, **kwargs)
        body = self.__body(instructions.requesting, bdata, claimed, **kwargs)

        request = adapter.build(url=url, method=instructions.method, params=query, body=body)
        log.info(f"(http.execute) built request: {request}")
        for i, hook in enumerate(prehooks:=instructions.hooks.before):
            log.debug(f"(http.execute) pre-hook [{i}/{len(prehooks)}]: {hook.__name__}")
            request = await hook(request)

        response = await adapter.send(request)
        log.debug(f"(http.execute) response: {response}")
        for i, hook in enumerate(posthooks:=instructions.hooks.after):
            log.debug(f"(http.execute) post-hook [{i}/{len(posthooks)}]: {hook.__name__}")
            response = await hook(response)

        return self.__response(instructions.responding, response)

execute = __execute()
