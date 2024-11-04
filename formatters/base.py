from typing import Any, Callable
from collections.abc import Iterable
from utils import *


class FieldErrorCode(IntEnum):
    MISSING = 100
    WRONG_TYPE = 101
    INVALID_PATTERN = 102
    LENGTH_NOT_IN_RANGE = 103
    NOT_IN_RANGE = 104

type PydanticError = dict[str, Any]
type DBError = GenericError
type FormattedError = tuple[IntEnum, str]
type ErrorTransformer[E] = Callable[[E], FormattedError | None]
type Result = dict[str, int | str | Result | list[Result]]
type SerializerErrorAppender = Callable[[PydanticError, Result, int], None]
type DBErrorAppender = Callable[[DBError, Result], None]


class BaseSerializerErrorAppender:
    def __init__(self, *, __root__: SerializerErrorAppender | None = None, **kwargs: SerializerErrorAppender):
        if __root__ is not None:
            self.__root__ = __root__
        for field, handler in kwargs.items():
            setattr(self, field, handler)

    def append_error(self, error: PydanticError, errors: Result, root: int) -> None:
        if len(error['loc']) == root + 1:
            self.__root__(error, errors, root)
            return
        field_name: str = error['loc'][root + 1]
        if not hasattr(self, field_name):
            raise ValueError(f'Unhandled serialization error at {error["loc"][root + 1]}')
        append_fn: SerializerErrorAppender = getattr(self, field_name)
        append_fn(error, errors, root)


class APISerializerErrorAppender(BaseSerializerErrorAppender):
    @staticmethod
    def __append_api_key_error(error: PydanticError, errors: Result, *args) -> None:
        if error['type'] == 'missing':
            e = (FieldErrorCode.MISSING, 'Missing API key')
        else:
            e = (FieldErrorCode.INVALID_PATTERN, 'Invalid API key')
        errors['api_key'] = {'type': e[0], 'message': e[1]}

    def __init__(self, **kwargs: SerializerErrorAppender):
        super().__init__(**kwargs)
        self.api_key = self.__append_api_key_error


class BaseSerializerFormatter:
    serializer_error_appender = BaseSerializerErrorAppender()

    @classmethod
    def append_serializer_error(cls, error: PydanticError, errors: Result, root: int = 0) -> None:
        cls.serializer_error_appender.append_error(error, errors, root)

    @classmethod
    def format_serializer_errors(cls, raw_errors: Iterable[PydanticError], root: int = 0) -> Result:
        errors: Result = {}
        for error in raw_errors:
            cls.append_serializer_error(error, errors, root)
        return errors


class BaseDBErrorAppender:
    def __init__(self, handlers: dict[IntEnum, Callable[[DBError, Result], None]]):
        self.handlers = {}
        for error, handler in handlers.items():
            self.handlers[error] = handler

    def append_error(self, error: DBError, errors: Result) -> None:
        if error.error_code not in self.handlers:
            raise ValueError(f'Unhandled database error {error.error_code}')
        self.handlers[error.error_code](error, errors)


class BaseDBFormatter:
    db_error_appender = BaseDBErrorAppender({})

    @classmethod
    def append_db_error(cls, error: DBError, errors: Result) -> None:
        cls.db_error_appender.append_error(error, errors)

    @classmethod
    def format_db_errors(cls, raw_errors: Iterable[DBError]) -> Result:
        errors: Result = {}
        for error in raw_errors:
            cls.append_db_error(error, errors)
        return errors


def append_serializer_field_error_factory(
    field_name: str, *,
    transformer: ErrorTransformer[PydanticError]
) -> SerializerErrorAppender:
    """Default field serializer error appender factory."""

    def append_fn(error: PydanticError, errors: Result, root: int) -> None:
        e = transformer(error)
        if e is None:
            raise ValueError(f'Unhandled serialization error: {error}')
        if field_name not in errors:
            errors[field_name] = []
        errors[field_name].append({'type': e[0], 'message': e[1]})

    return append_fn

def append_serializer_list_error_factory(
    list_field_name: str, transformer: ErrorTransformer[PydanticError],
    element_transformer: ErrorTransformer[PydanticError]
) -> SerializerErrorAppender:
    """Default list field serializer error appender factory."""

    def append_fn(error: PydanticError, errors: Result, root: int) -> None:
        if len(error['loc']) == root + 2:  # Excludes possibility for inner errors
            e = transformer(error)
            if e is None:
                raise ValueError(f'Unhandled serialization error: {error}')
            errors[list_field_name] = {'type': e[0], 'message': e[1]}
            return
        e = element_transformer(error)
        if e is None:
            raise ValueError(f'Unhandled serialization error: {error}')
        if list_field_name not in errors:
            errors[list_field_name] = {}
        element_index = str(error['loc'][root + 2])
        if element_index not in errors[list_field_name]:
            errors[list_field_name][element_index] = []
        errors[list_field_name][element_index].append({'type': e[0], 'message': e[1]})

    return append_fn

def append_db_field_error_factory(
    field_name: str, *,
    transformer: ErrorTransformer[DBError]
) -> DBErrorAppender:
    """Default field database error appender factory."""

    def append_fn(error: DBError, errors: Result) -> None:
        e = transformer(error)
        if e is None:
            raise ValueError(f'Unhandled database error: {error}')
        if field_name not in errors:
            errors[field_name] = []
        errors[field_name].append({'type': e[0], 'message': e[1]})

    return append_fn

def transform_id_error_factory(human_field_name: str) -> ErrorTransformer[PydanticError]:
    """Default id field transformer factory. If your field is named 'user_id', then 'human_field_name'
       should be 'User id'."""

    def transform_fn(error: PydanticError) -> FormattedError | None:
        match error['type']:
            case 'missing':
                return FieldErrorCode.MISSING, 'Missing required field'
            case 'int_type':
                return FieldErrorCode.WRONG_TYPE, f'{human_field_name} must be an int'
            case 'greater_than_equal':
                return FieldErrorCode.NOT_IN_RANGE, f'{human_field_name} must be greater than or equal to 1'

    return transform_fn

def transform_str_error_factory(human_field_name: str, *, min_length: int = 0, max_length: int) \
        -> ErrorTransformer[PydanticError]:
    """Default string field error transformer factory. If your field is named 'surname', then 'human_field_name'
       should be 'Surname'."""

    def transform_fn(error: PydanticError) -> FormattedError | None:
        match error['type']:
            case 'missing':
                return FieldErrorCode.MISSING, 'Missing required field'
            case 'string_type':
                return FieldErrorCode.WRONG_TYPE, f'{human_field_name} must be a string'
            case 'string_too_short' | 'string_too_long':
                return FieldErrorCode.LENGTH_NOT_IN_RANGE, \
                    f'{human_field_name} must contain from {min_length} to {max_length} characters'

    return transform_fn

def transform_list_error_factory(human_list_field_name: str) -> ErrorTransformer[PydanticError]:
    """Default list field error transformer factory. If your field is named 'tag_ids', then 'human_list_field_name'
       should be 'Tag ids'."""

    def transform_fn(error: PydanticError) -> FormattedError:
        match error['type']:
            case 'missing':
                return FieldErrorCode.MISSING, 'Missing requred field'
            case 'list_type':
                return FieldErrorCode.WRONG_TYPE, f'{human_list_field_name} must be a list'

    return transform_fn
