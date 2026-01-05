# ~/clientity/src/clientity/core/utils/http.py
from __future__ import annotations
import typing as t

from urllib.parse import urlparse

from clientity.logs import log
from clientity.core.hints import Requested, Embodied
from clientity.core.protocols import Requestable


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

    return "json", obj


def domain(url: str) -> str:
    parsed = urlparse(url)
    splits = parsed.path.split('/')[0]
    value = (parsed.netloc or splits)
    log.debug(f"(domain) parsed {url} -> {value}")
    return value
