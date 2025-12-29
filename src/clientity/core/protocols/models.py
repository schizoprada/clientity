# ~/clientity/src/clientity/core/protocols/models.py
from __future__ import annotations
import typing as t

from clientity.core.hints import ResponseObject

@t.runtime_checkable
class Requestable(t.Protocol):
    def __request__(self) -> t.Union[dict, bytes]: ...

@t.runtime_checkable
class Responsive(t.Protocol):
    @classmethod
    def __respond__(cls, response: ResponseObject) -> t.Self: ...
