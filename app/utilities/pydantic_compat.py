from __future__ import annotations

from typing import TYPE_CHECKING, Callable

try:  # pragma: no cover - pydantic v1 compatibility
    from pydantic import BaseModel

    if not hasattr(BaseModel, "model_dump"):
        from typing import Callable

        def _model_dump(self: BaseModel, **kwargs) -> dict:
            return BaseModel.dict(self, **kwargs)

        setattr(BaseModel, "model_dump", _model_dump)  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - ignore if pydantic v2
    pass

if TYPE_CHECKING:
    from pydantic import field_validator, model_validator  # type: ignore
else:  # pragma: no cover - runtime fallback for pydantic v1
    try:
        from pydantic import field_validator, model_validator  # type: ignore
    except ImportError:  # pragma: no cover - pydantic v1
        from pydantic import validator, root_validator

        def field_validator(*fields: str, **kwargs) -> Callable:
            kwargs.pop("mode", None)
            return validator(*fields, **kwargs)

        def model_validator(*fields, **kwargs) -> Callable:
            mode = kwargs.pop("mode", "after")

            def decorator(func: Callable) -> Callable:
                if mode == "after":

                    def wrapper(cls, values):
                        obj = cls.construct(**values)
                        func(obj)
                        return obj.dict()

                    return root_validator(pre=False, allow_reuse=True)(wrapper)

                def wrapper(cls, values):
                    return func(values)

                return root_validator(pre=True, allow_reuse=True)(wrapper)

            return decorator
