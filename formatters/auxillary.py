from formatters.base import *
from utils import *

from models.auxillary.address import CreateCountryErrorCode


class Date(BaseSerializerFormatter):
    class ErrorCode(IntEnum):
        INVALID_DATE = 200

    @staticmethod
    def append_root_error(error: PydanticError, errors: ErrorTrace, root: int) -> None:
        errors['type'] = Date.ErrorCode.INVALID_DATE
        errors['message'] = 'Invalid combination of year, month and day'

    @staticmethod
    def transform_day_error(error: PydanticError, _root: int) -> FormattedError | None:
        match error['type']:
            case 'missing':
                return FieldErrorCode.MISSING, 'Missing required field'
            case 'int_type':
                return FieldErrorCode.WRONG_TYPE, 'Day must be an int'
            case 'less_than_equal' | 'greater_than_equal':
                return FieldErrorCode.NOT_IN_RANGE, 'Day must be in range from 1 to 31'

    @staticmethod
    def transform_month_error(error: PydanticError, _root: int) -> FormattedError | None:
        match error['type']:
            case 'missing':
                return FieldErrorCode.MISSING, 'Missing required field'
            case 'int_type':
                return FieldErrorCode.WRONG_TYPE, 'Month must be an int'
            case 'less_than_equal' | 'greater_than_equal':
                return FieldErrorCode.NOT_IN_RANGE, 'Month must be in range from 1 to 12'

    @staticmethod
    def transform_year_error(error: PydanticError, _root: int) -> FormattedError | None:
        match error['type']:
            case 'missing':
                return FieldErrorCode.MISSING, 'Missing required field'
            case 'int_type':
                return FieldErrorCode.WRONG_TYPE, 'Year must be an int'
            case 'greater_than_equal':
                return FieldErrorCode.NOT_IN_RANGE, 'Year must be greater than or equal to 1900'

    serializer_error_appender = BaseSerializerErrorAppender(
        __root__=append_root_error,
        day=append_serializer_field_error_factory(transform_day_error),
        month=append_serializer_field_error_factory(transform_month_error),
        year=append_serializer_field_error_factory(transform_year_error),
    )


class GetCountryByIDFormatter:
    """Convenience class with DB error message."""

    @classmethod
    def get_db_error(cls, *, code: int) -> ErrorTrace:
        return {'country_id': [{'type': code, 'message': 'Country with provided id doesn\'t exist'}]}

class CreateCountryFormatter(BaseSerializerFormatter, BaseDBFormatter):
    class ErrorCode(IntEnum):
        NON_UNIQUE_NAME = 200

    serializer_error_appender = RootSerializerErrorAppender(
        query=APISerializerErrorAppender().append_error,
        body=BaseSerializerErrorAppender(
            name=append_serializer_field_error_factory(transform_str_error_factory('Country name',
                                                                                   min_length=1, max_length=50)),
            phone_code=append_serializer_field_error_factory(transform_int_error_factory('Phone code', ge=1, le=999)),
        ).append_error,
    )

    @staticmethod
    def transform_non_unique_name_error(*_) -> FormattedError:
        return CreateCountryFormatter.ErrorCode.NON_UNIQUE_NAME, 'Country with given name already exists'

    db_error_appender = BaseDBErrorAppender({
        CreateCountryErrorCode.NON_UNIQUE_NAME:
            append_db_field_error_factory(field_name='name', transformer=transform_non_unique_name_error),
    })


class CreateCityFormatter(BaseSerializerFormatter, BaseDBFormatter):
    serializer_error_appender = RootSerializerErrorAppender(
        query=APISerializerErrorAppender(
            country_id=append_serializer_field_error_factory(transform_id_error_factory('Country id')),
        ).append_error,
        body=BaseSerializerErrorAppender(
            name=append_serializer_field_error_factory(transform_str_error_factory('City name',
                                                                                   min_length=1, max_length=50)),
        ).append_error,
    )
