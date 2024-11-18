from typing import Any, Callable, Self
from collections.abc import Iterable

from utils import *


class FieldErrorCode(IntEnum):
    # Pydantic
    MISSING = 100
    WRONG_TYPE = 101
    INVALID_PATTERN = 102
    LENGTH_NOT_IN_RANGE = 103
    NOT_IN_RANGE = 104
    MISSING_DISCRIMINATOR = 105
    INVALID_DISCRIMINATOR = 106
    # DB
    INVALID_API_KEY = 150
    INSUFFICIENT_PERMISSIONS = 151

type FormattedError = tuple[IntEnum, str]
type ErrorTrace = dict[str, ErrorTrace | list[ErrorTrace]]
type ErrorTransformer[E, C] = Callable[[E, C], FormattedError | None]
type ErrorAppender[E, C] = Callable[[E, ErrorTrace, C], None]

type PydanticError = dict[str, Any]
type SerializerErrorTransformer = ErrorTransformer[PydanticError, int]
type SerializerErrorAppender = ErrorAppender[PydanticError, int]

type DBError = GenericError
type DBErrorTransformer = ErrorTransformer[DBError, None]
type DBErrorAppender = ErrorAppender[DBError, None]


class BaseSerializerErrorAppender:
    def __init__(self, *, __root__: SerializerErrorAppender | None = None, **kwargs: SerializerErrorAppender):
        if __root__ is not None:
            self.__root__ = __root__
        for field, handler in kwargs.items():
            setattr(self, field, handler)

    def add_field_error_appender(self, field: str, error_appender: SerializerErrorAppender) -> Self:
        setattr(self, field, error_appender)
        return self

    def append_error(self, error: PydanticError, errors: ErrorTrace, root: int) -> None:
        if len(error['loc']) == root + 1:
            self.__root__(error, errors, root)
            return
        field_name: str = error['loc'][root + 1]
        if not hasattr(self, field_name):
            raise ValueError(f'Unhandled serialization error {error}')
        append_fn: ErrorAppender[PydanticError, int] = getattr(self, field_name)
        append_fn(error, errors, root)

class RootSerializerErrorAppender(BaseSerializerErrorAppender):
    def append_error(self, error: PydanticError, errors: ErrorTrace, root: int) -> None:
        branch_name: str = error['loc'][root]
        if not hasattr(self, branch_name):
            raise ValueError(f'Unhandled serialization error: {error}')
        append_fn: ErrorAppender[PydanticError, int] = getattr(self, branch_name)
        append_fn(error, errors, root)

class APISerializerErrorAppender(BaseSerializerErrorAppender):
    @staticmethod
    def transform_api_key_error(error: PydanticError, _root: int) -> FormattedError | None:
        match error['type']:
            case 'missing':
                return FieldErrorCode.MISSING, 'Missing required field'
            case _:
                return FieldErrorCode.INVALID_PATTERN, 'Invalid API key'

    @staticmethod
    def transform_invalid_api_key_error(*_) -> FormattedError:
        return FieldErrorCode.INVALID_API_KEY, 'Invalid API key provided'

    def __init__(self, **kwargs: SerializerErrorAppender):
        super().__init__(**kwargs)
        self.api_key = append_serializer_field_error_factory(self.transform_api_key_error)


class BaseSerializerFormatter:
    serializer_error_appender = BaseSerializerErrorAppender()

    @classmethod
    def append_serializer_error(cls, error: PydanticError, errors: ErrorTrace, root: int = 0) -> None:
        cls.serializer_error_appender.append_error(error, errors, root)

    @classmethod
    def format_serializer_errors(cls, raw_errors: Iterable[PydanticError], root: int = 0) -> ErrorTrace:
        errors: ErrorTrace = {}
        for error in raw_errors:
            cls.append_serializer_error(error, errors, root)
        return errors


class BaseDBErrorAppender:
    def __init__(self, handlers: dict[IntEnum, DBErrorAppender]):
        self.handlers = {}
        for error, handler in handlers.items():
            self.handlers[error] = handler

    def append_error(self, error: DBError, errors: ErrorTrace) -> None:
        if error.error_code not in self.handlers:
            raise ValueError(f'Unhandled database error {error.error_code}')
        self.handlers[error.error_code](error, errors, None)


class BaseDBFormatter:
    db_error_appender = BaseDBErrorAppender({})

    @classmethod
    def append_db_error(cls, error: DBError, errors: ErrorTrace) -> None:
        cls.db_error_appender.append_error(error, errors)

    @classmethod
    def format_db_errors(cls, raw_errors: Iterable[DBError]) -> ErrorTrace:
        errors: ErrorTrace = {}
        for error in raw_errors:
            cls.append_db_error(error, errors)
        return errors


def get_serializer_error_field_name(error: PydanticError, root: int) -> str:
    field_name: str | int = error['loc'][root + 1]
    if isinstance(field_name, int):
        return str(field_name)
    return field_name

def append_serializer_field_error_factory(transformer: SerializerErrorTransformer) -> SerializerErrorAppender:
    """Default field serializer error appender factory."""

    def append_fn(error: PydanticError, errors: ErrorTrace, root: int) -> None:
        e = transformer(error, root)
        if e is None:
            raise ValueError(f'Unhandled serialization error: {error}')
        field_name = get_serializer_error_field_name(error, root)
        if field_name not in errors:
            errors[field_name] = []
        errors[field_name].append({'type': e[0], 'message': e[1]})

    return append_fn

def append_serializer_list_error_factory(
    transformer: SerializerErrorTransformer, element_error_appender: SerializerErrorAppender
) -> SerializerErrorAppender:
    """Default list field serializer error appender factory."""

    def append_fn(error: PydanticError, errors: ErrorTrace, root: int) -> None:
        if len(error['loc']) == root + 2:  # Excludes possibility for inner errors
            e = transformer(error, root)
            if e is None:
                raise ValueError(f'Unhandled serialization error: {error}')
            errors[get_serializer_error_field_name(error, root)] = [{'type': e[0], 'message': e[1]}]
            return
        list_field_name = get_serializer_error_field_name(error, root)
        if list_field_name not in errors:
            errors[list_field_name] = {}
        element_error_appender(error, errors[list_field_name], root + 1)

    return append_fn

def append_db_field_error_factory(
    field_name: str, *,
    transformer: DBErrorTransformer
) -> DBErrorAppender:
    """Default field database error appender factory."""

    def append_fn(error: DBError, errors: ErrorTrace, _) -> None:
        e = transformer(error, None)
        if e is None:
            raise ValueError(f'Unhandled database error: {error}')
        if field_name not in errors:
            errors[field_name] = []
        errors[field_name].append({'type': e[0], 'message': e[1]})

    return append_fn

def transform_id_error_factory(human_field_name: str) -> SerializerErrorTransformer:
    """Default id field transformer factory. If your field is named 'user_id', then 'human_field_name'
       should be 'User id'."""

    def transform_fn(error: PydanticError, _root: int) -> FormattedError | None:
        match error['type']:
            case 'missing':
                return FieldErrorCode.MISSING, 'Missing required field'
            case 'int_type':
                return FieldErrorCode.WRONG_TYPE, f'{human_field_name} must be an int'
            case 'greater_than_equal':
                return FieldErrorCode.NOT_IN_RANGE, f'{human_field_name} must be greater than or equal to 1'

    return transform_fn

def transform_int_error_factory(human_field_name: str, *, ge: int | None = None, le: int | None = None) \
        -> SerializerErrorTransformer:
    """Default integer field error transformer factory. If your field is named 'max_length', then 'human_field_name'
       should be 'Max length'."""

    def transform_fn(error: PydanticError, _root: int) -> FormattedError | None:
        match error['type']:
            case 'missing':
                return FieldErrorCode.MISSING, 'Missing required field'
            case 'int_type':
                return FieldErrorCode.WRONG_TYPE, f'{human_field_name} must be an int'
            case 'greater_than_equal':
                return FieldErrorCode.NOT_IN_RANGE, f'{human_field_name} must be greater than or equal to {ge}'
            case 'less_than_equal':
                return FieldErrorCode.NOT_IN_RANGE, f'{human_field_name} must be lesser than or equal to {le}'

    return transform_fn

def transform_bool_error_factory(human_field_name: str) -> SerializerErrorTransformer:
    """Default boolean field error transformer factory. If your field is named 'is_requred', then 'hunam_field_name'
       should be 'Is required'."""

    def transform_fn(error: PydanticError, _root: int) -> FormattedError | None:
        match error['type']:
            case 'missing':
                return FieldErrorCode.MISSING, 'Missing required field'
            case 'bool_type':
                return FieldErrorCode.WRONG_TYPE, f'{human_field_name} must be a boolean'

    return transform_fn

def transform_str_error_factory(human_field_name: str, *, min_length: int | None = None,
                                max_length: int | None = None) -> SerializerErrorTransformer:
    """Default string field error transformer factory. If your field is named 'surname', then 'human_field_name'
       should be 'Surname'."""

    def transform_fn(error: PydanticError, _root: int) -> FormattedError | None:
        match error['type']:
            case 'missing':
                return FieldErrorCode.MISSING, 'Missing required field'
            case 'string_type':
                return FieldErrorCode.WRONG_TYPE, f'{human_field_name} must be a string'
            case 'string_too_short' | 'string_too_long':
                return FieldErrorCode.LENGTH_NOT_IN_RANGE, \
                    f'{human_field_name} must contain from {min_length} to {max_length} characters'

    return transform_fn

def transform_http_url_error_factory(human_field_name: str, *, max_length: int | None = None) \
        -> SerializerErrorTransformer:
    """Default http url field error transformer factory. If your field is named 'link', then 'human_field_name'
       should be 'Link'."""

    def transform_fn(error: PydanticError, _root: int) -> FormattedError | None:
        match error['type']:
            case 'missing':
                return FieldErrorCode.MISSING, 'Missing required field'
            case 'url_type':
                return FieldErrorCode.WRONG_TYPE, f'{human_field_name} must be a string-encoded URL'
            case 'url_parsing' | 'url_scheme':
                return FieldErrorCode.INVALID_PATTERN, f'{human_field_name} must be a valid HTTP URL'
            case 'string_too_long':
                return (FieldErrorCode.LENGTH_NOT_IN_RANGE, f'{human_field_name} can contain at most {max_length}'
                                                            f'characters')

    return transform_fn

def transform_list_error_factory(human_list_field_name: str, *, min_length: int | None = None,
                                 max_length: int | None = None) -> SerializerErrorTransformer:
    """Default list field error transformer factory. If your field is named 'tag_ids', then 'human_list_field_name'
       should be 'Tag ids'."""

    def transform_fn(error: PydanticError, _root: int) -> FormattedError | None:
        match error['type']:
            case 'missing':
                return FieldErrorCode.MISSING, 'Missing requred field'
            case 'list_type':
                return FieldErrorCode.WRONG_TYPE, f'{human_list_field_name} must be a list'
            case 'too_short':
                return (FieldErrorCode.LENGTH_NOT_IN_RANGE, f'{human_list_field_name} must contain at least '
                                                            f'{min_length} item(s)')
            case 'too_long':
                return (FieldErrorCode.LENGTH_NOT_IN_RANGE, f'{human_list_field_name} can contain at most {max_length} '
                                                            f'item(s)')

    return transform_fn

class append_tagged_union_error:
    def __init__(self, root_error_transformer: SerializerErrorTransformer):
        self.__root__ = root_error_transformer

    def add_variant_error_appender(self, tag: str, error_appender: SerializerErrorAppender) -> Self:
        setattr(self, tag, error_appender)
        return self

    def __call__(self, error: PydanticError, errors: ErrorTrace, root: int) -> None:
        if len(error['loc']) == root + 2:  # Excludes possibility for inner errors
            e = self.__root__(error, root)
            if e is None:
                raise ValueError(f'Unhandled serialization error: {error}')
            errors[get_serializer_error_field_name(error, root)] = [{'type': e[0], 'message': e[1]}]
            return
        tag: str = error['loc'][root + 2]
        if not hasattr(self, tag):
            raise ValueError(f'Unhandled union variant: {tag}')
        union_field_name = get_serializer_error_field_name(error, root)
        if union_field_name not in errors:
            errors[union_field_name] = {}
        appender: SerializerErrorAppender = getattr(self, tag)
        appender(error, errors[union_field_name], root + 2)

def transform_tagged_union_error_factory(human_union_field_name: str) -> SerializerErrorTransformer:
    """Default tagged union field error transformer factory. If your field is named 'fields', then
       'human_union_field_name' should be 'Fields'."""

    def transform_fn(error: PydanticError, _root: int) -> FormattedError | None:
        match error['type']:
            case 'missing':
                return FieldErrorCode.MISSING, 'Missing required field'
            case 'union_tag_not_found':
                return (FieldErrorCode.MISSING_DISCRIMINATOR, f'{human_union_field_name} misses a discriminator field '
                                                              f'{error["ctx"]["discriminator"]}')
            case 'union_tag_invalid':
                return (FieldErrorCode.INVALID_DISCRIMINATOR, f'{human_union_field_name} has invalid discriminator '
                                                              f'value.')

    return transform_fn

def append_nested_model_error_factory(
    transformer: SerializerErrorTransformer, model_error_appender: SerializerErrorAppender
) -> SerializerErrorAppender:
    """Default nested model field serializer error appender factory."""

    def append_fn(error: PydanticError, errors: ErrorTrace, root: int) -> None:
        if len(error['loc']) == root + 2:  # Excludes possibility for inner errors
            e = transformer(error, root)
            if e is None:
                raise ValueError(f'Unhandled serialization error: {error}')
            errors[get_serializer_error_field_name(error, root)] = [{'type': e[0], 'message': e[1]}]
            return
        model_field_name = get_serializer_error_field_name(error, root)
        if model_field_name not in errors:
            errors[model_field_name] = {}
        model_error_appender(error, errors[model_field_name], root + 1)

    return append_fn

def transform_nested_model_error_factory(human_model_field_name: str) -> SerializerErrorTransformer:
    """Default nested model field error transformer factory. If your field is named 'fields', then
       'human_model_field_name' should be 'Fields'."""

    def transform_fn(error: PydanticError, _root: int) -> FormattedError | None:
        match error['type']:
            case 'missing':
                return FieldErrorCode.MISSING, 'Missing required field'
            case 'model_attributes_type':
                return FieldErrorCode.WRONG_TYPE, f'{human_model_field_name} must be a dictionary'

    return transform_fn

def transform_uuid_error_factory(human_field_name: str) -> SerializerErrorTransformer:
    """Default UUID field error transformer factory. If your field is named 'fields', then 'human_field_name'
       should be 'Fields'."""

    def transform_fn(error: PydanticError, _root: int) -> FormattedError | None:
        match error['type']:
            case 'missing':
                return FieldErrorCode.MISSING, 'Missing required field'
            case 'uuid_parsing' | 'uuid_type':
                return FieldErrorCode.WRONG_TYPE, f'{human_field_name} must be a valid string encoded UUID'
            case 'uuid_version':
                return (FieldErrorCode.WRONG_TYPE, f'{human_field_name} must be a valid UUID version '
                                                   f'{error["ctx"]["expected_version"]}')

    return transform_fn
