from enum import IntEnum
from typing import Any, Callable
from collections.abc import Iterable
from abc import ABC, abstractmethod

class FieldErrorCode(IntEnum):
    MISSING = 100
    WRONG_TYPE = 101
    INVALID_PATTERN = 102
    TOO_SHORT = 103
    TOO_LONG = 104
    NOT_IN_RANGE = 105

type PydanticError = dict[str, Any]
type Result = dict[str, int | dict[str, Result] | list[dict[str, Result]]]

class BaseSerializerFormatter(ABC):
    @classmethod
    def append_serializer_field_error(
        cls, error: PydanticError, errors: Result, *,
        field_name: str, matcher: Callable[[str], tuple[int, str] | None]
    ) -> None:
        e = matcher(error['type'])
        if e is None:
            raise ValueError(f'Unhandled serialization error {error["type"]}')
        if field_name not in errors:
            errors[field_name] = []
        errors[field_name].append({ 'type': e[0], 'message': e[1] })

    @classmethod
    @abstractmethod
    def append_serializer_error(cls, error: PydanticError, errors: Result,
                                root: int = 0) -> None: ...

    @classmethod
    def format_serializer_errors(cls, raw_errors: Iterable[PydanticError],
                                 root: int = 0) -> Result:
        errors: Result = {}
        for error in raw_errors:
            cls.append_serializer_error(error, errors)
        return errors
