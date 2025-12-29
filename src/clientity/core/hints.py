# ~/clientity/src/clientity/core/hints.py
from __future__ import annotations
import typing as t, types as ts, typing_extensions as tx

_T = t.TypeVar("_T")

ResponseObject = t.TypeVar("ResponseObject")
RO = ResponseObject


class Callable:
    Sync = t.Callable[..., _T]
    Async = t.Callable[..., t.Awaitable[_T]]

Call = t.Union[
    Callable.Sync,
    Callable.Async
]

Embodied = tuple[str, t.Union[dict, bytes]]

if t.TYPE_CHECKING:
    from clientity.core.protocols.models import Requestable, Responsive

Requesting = t.Union[None, t.Any, 'Requestable']
Responding = t.Union[None, t.Type[ResponseObject], t.Type['Responsive']]
