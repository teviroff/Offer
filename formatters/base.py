from enum import IntEnum
from typing import Any
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

class BaseFormatter(ABC):
    @classmethod
    @abstractmethod
    def add_error(cls, error: PydanticError, errors: Result, root: int = 0) -> None:
        ...

    @classmethod
    def format_serializer_errors(cls, raw_errors: Iterable[PydanticError],
                                 root: int = 0) -> Result:
        errors: Result = {'stage': 0} if root == 0 else {}
        for error in raw_errors:
            cls.add_error(error, errors)
        return errors
