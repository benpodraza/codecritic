from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from pydantic import field_validator, model_validator  # type: ignore
else:  # pragma: no cover - runtime fallback for pydantic v1
    try:
        from pydantic import field_validator, model_validator  # type: ignore
    except ImportError:  # pragma: no cover - pydantic v1
        from pydantic import validator

        def field_validator(*fields: str, **kwargs) -> Callable:
            return validator(*fields, **kwargs)

        def model_validator(*fields, **kwargs) -> Callable:
            return validator(*fields, **kwargs)
