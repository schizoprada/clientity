# ~/clientity/src/clientity/core/utils/models.py
from __future__ import annotations
import typing as t, dataclasses as dc

from clientity.exc import ModelingError, ResponseError
from clientity.logs import log
from clientity.core.hints import (
    Responding, Responded,
    ResponseType, ResponseObject
)
from clientity.core.protocols import Responsive

class __constructors:
    __known__: tuple[tuple[str, str], ...] = (
        ('model_fields', 'annotation'), # pydantic v2
        ('__fields__', 'outer_type_'), # pydantic v1
        ('__dataclass_fields__', 'type') # dataclasses
    )

    def __call__(self, model: t.Any) -> dict[str, type]:
        if model is None: return {}
        for mattr, fattr in self.__known__:
            if (mapping:=getattr(model, mattr, {})):
                log.debug(f"(constructors.__call__) identified mapping for model [{model.__name__}]: {mattr}")
                return {
                    name: getattr(f, fattr) for
                    name, f in mapping.items()
                }
        if (annotated:=getattr(model, '__annotations__')):
            log.debug(f"(constructors.__call__) falling back to annotations for model: {model.__name__}")
            return dict(annotated)

        log.warning(f"(constructors.__call__) could not identify constructor mapping for model: {model.__name__}")
        return {}

constructors = __constructors()


class __dictate:
    __known__: tuple[tuple[str, t.Callable[..., dict]], ...] = (
        ("model_dump", lambda m: m.model_dump()),
        ("dict", lambda m: m.dict()),
        ("__dataclass_fields__", dc.asdict),
        ("__dict__", lambda m: m.__dict__)
    )

    def __call__(self, obj: t.Any) -> dict:
        if obj is None: return {}
        for attr, method in self.__known__:
            if hasattr(obj, attr):
                return method(obj)
        return dict(obj)

dictate = __dictate()


class __respond:
    @t.overload
    def __call__(self, model: None, response: ResponseObject) -> None: ...
    @t.overload
    def __call__(self, model: ResponseType, response: ResponseObject) -> ResponseType: ...
    def __call__(
        self,
        model: Responding,
        response: ResponseObject
        ) -> Responded:
        if model is None: return None
        if issubclass(model, Responsive):
            try:
                return model.__respond__(response)
            except Exception as e:
                raise ModelingError(f"Failed to instantiate model ({model.__name__}) from response") from e

        if (rbody:=getattr(response, 'json', None)):
            if callable(rbody):
                try:
                    data = rbody()
                except Exception as e:
                    raise ResponseError(f"Failed to parse json data") from e

                try:
                    return model(**t.cast(dict, data))
                except Exception as e:
                    raise ModelingError(f"Failed to instantiate model ({model.__name__})") from e

        raise ModelingError(f"No JSON method available in response") # not sure what to write here lol
respond = __respond()
