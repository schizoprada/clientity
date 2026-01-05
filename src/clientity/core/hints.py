# ~/clientity/src/clientity/core/hints.py
from __future__ import annotations
import typing as t, types as ts, typing_extensions as tx

_T = t.TypeVar("_T")
class Callable:
    Sync = t.Callable[..., _T]
    Async = t.Callable[..., t.Awaitable[_T]]

type Call = t.Union[
    Callable.Sync,
    Callable.Async
]

Synced = t.Union[Callable.Sync, t.Any]
Asynced = t.Union[Callable.Async, t.Any]


RequestObject = t.TypeVar("RequestObject")
ResponseObject = t.TypeVar("ResponseObject")

type Embodied = tuple[str, t.Union[dict, bytes]]

if t.TYPE_CHECKING:
    from clientity.core.protocols.models import Requestable, Responsive

Requesting = t.Union[None, t.Any, t.Type['Requestable']]
Responding = t.Union[None, t.Type[ResponseObject], t.Type['Responsive']]
Responded = t.Union[ResponseObject, 'Responsive']
Requested = t.Union['Requestable', dict, bytes, t.Any]
