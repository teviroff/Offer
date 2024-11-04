from formatters.base import *
from utils import *
from formatters.auxillary import Date
from models.user import CreateUserErrorCode, UpdateUserInfoErrorCode, DeleteCVErrorCode


class CreateUserFormatter(BaseSerializerFormatter, BaseDBFormatter):
    class ErrorCode(IntEnum):
        NON_UNIQUE_EMAIL = 200

    @staticmethod
    def transform_email_error(error: PydanticError) -> FormattedError | None:
        match error['type']:
            case 'missing':
                return FieldErrorCode.MISSING, 'Missing required field'
            case 'string_type':
                return FieldErrorCode.WRONG_TYPE, 'Email must be a string'
            case 'pattern_error':
                return FieldErrorCode.INVALID_PATTERN, 'Not a valid email address'

    @staticmethod
    def transform_password_error(error: PydanticError) -> FormattedError | None:
        match error['type']:
            case 'missing':
                return FieldErrorCode.MISSING, 'Missing required field'
            case 'string_type':
                return FieldErrorCode.WRONG_TYPE, 'Password must be a string'
            case 'string_too_short':
                return FieldErrorCode.LENGTH_NOT_IN_RANGE, 'Password must contain at least 8 characters'
            case 'pattern_error':
                return FieldErrorCode.INVALID_PATTERN, 'Password must contain at least one lowercase letter, ' \
                                                       'one uppercase letter, one digit and one special character'

    serializer_error_appender = APISerializerErrorAppender(
        email=append_serializer_field_error_factory('email', transformer=transform_email_error),
        password=append_serializer_field_error_factory('password', transformer=transform_password_error),
    )

    @staticmethod
    def transform_non_unique_email_error(_) -> FormattedError:
        return CreateUserFormatter.ErrorCode.NON_UNIQUE_EMAIL, 'User with provided email already exists'

    db_error_appender = BaseDBErrorAppender({
        CreateUserErrorCode.NON_UNIQUE_EMAIL:
            append_db_field_error_factory('email', transformer=transform_non_unique_email_error),
    })


class UpdateUserInfoFormatter(BaseSerializerFormatter, BaseDBFormatter):
    class ErrorCode(IntEnum):
        INVALID_USER_ID = 200

    @staticmethod
    def append_birthday_error(error: PydanticError, errors: Result, root: int) -> None:
        e = None
        match error['type']:
            case 'model_attributes_type':
                e = (FieldErrorCode.WRONG_TYPE, 'Birthday must be a dictionary')
        if e is not None:  # Excludes possibility for inner errors
            errors['birthday'] = {'type': e[0], 'message': e[1]}
            return
        if 'birthday' not in errors:
            errors['birthday'] = {}
        Date.append_serializer_error(error, errors['birthday'], root + 1)

    serializer_error_appender = APISerializerErrorAppender(
        user_id=append_serializer_field_error_factory(
            field_name='user_id',
            transformer=transform_id_error_factory('User id')
        ),
        name=append_serializer_field_error_factory(
            field_name='name',
            transformer=transform_str_error_factory('Name', min_length=1, max_length=50)
        ),
        surname=append_serializer_field_error_factory(
            field_name='surname',
            transformer=transform_str_error_factory('Surname', min_length=1, max_length=50)
        ),
        birthday=append_birthday_error,
        city_id=append_serializer_field_error_factory(
            field_name='city_id',
            transformer=transform_id_error_factory('City id')
        ),
    )

    @staticmethod
    def transform_invalid_user_id_error(_) -> FormattedError:
        return UpdateUserInfoFormatter.ErrorCode.INVALID_USER_ID, 'User with provided id doesn\'t exist'

    db_error_appender = BaseDBErrorAppender({
        UpdateUserInfoErrorCode.INVALID_USER_ID:
            append_db_field_error_factory('user_id', transformer=transform_invalid_user_id_error),
    })


class DeleteUserCVFormatter(BaseSerializerFormatter, BaseDBFormatter):
    class ErrorCode(IntEnum):
        INVALID_CV_ID = 200

    serializer_error_appender = APISerializerErrorAppender(
        cv_id=append_serializer_field_error_factory('cv_id', transformer=transform_id_error_factory('CV id'))
    )

    @staticmethod
    def transform_invalid_cv_id_error(_) -> FormattedError:
        return DeleteUserCVFormatter.ErrorCode.INVALID_CV_ID, 'CV with provided id doesn\'t exist'

    db_error_appender = BaseDBErrorAppender({
        DeleteCVErrorCode.INVALID_CV_ID:
            append_db_field_error_factory('cv_id', transformer=transform_invalid_cv_id_error),
    })
