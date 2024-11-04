from formatters.base import *
from utils import *


class Date(BaseSerializerFormatter):
    class ErrorCode(IntEnum):
        INVALID_DATE = 200

    @staticmethod
    def append_root_error(error: PydanticError, errors: Result, root: int) -> None:
        errors['type'] = Date.ErrorCode.INVALID_DATE
        errors['message'] = 'Invalid combination of year, month and day'

    @staticmethod
    def transform_day_error(error: PydanticError) -> FormattedError | None:
        match error['type']:
            case 'missing':
                return FieldErrorCode.MISSING, 'Missing required field'
            case 'int_type':
                return FieldErrorCode.WRONG_TYPE, 'Day must be an int'
            case 'less_than_equal' | 'greater_than_equal':
                return FieldErrorCode.NOT_IN_RANGE, 'Day must be in range from 1 to 31'

    @staticmethod
    def transform_month_error(error: PydanticError) -> FormattedError | None:
        match error['type']:
            case 'missing':
                return FieldErrorCode.MISSING, 'Missing required field'
            case 'int_type':
                return FieldErrorCode.WRONG_TYPE, 'Month must be an int'
            case 'less_than_equal' | 'greater_than_equal':
                return FieldErrorCode.NOT_IN_RANGE, 'Month must be in range from 1 to 12'

    @staticmethod
    def transform_year_error(error: PydanticError) -> FormattedError | None:
        match error['type']:
            case 'missing':
                return FieldErrorCode.MISSING, 'Missing required field'
            case 'int_type':
                return FieldErrorCode.WRONG_TYPE, 'Year must be an int'
            case 'greater_than_equal':
                return FieldErrorCode.NOT_IN_RANGE, 'Year must be greater than or equal to 1900'

    serializer_error_appender = BaseSerializerErrorAppender(
        __root__=append_root_error,
        day=append_serializer_field_error_factory('day', transformer=transform_day_error),
        month=append_serializer_field_error_factory('month', transformer=transform_month_error),
        year=append_serializer_field_error_factory('year', transformer=transform_year_error),
    )
