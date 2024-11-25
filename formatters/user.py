from formatters.base import *
from utils import *
from formatters.auxillary import Date
from models.user import (
    CreateUserErrorCode, UpdateUserInfoErrorCode, UpdateAvatarErrorCode,
    DeleteCVErrorCode, AddCVErrorCode,
)


class GetAPIKeyFormatter(BaseSerializerFormatter):
    serializer_error_appender = BaseSerializerErrorAppender(
        key=append_serializer_field_error_factory(APISerializerErrorAppender.transform_api_key_error),
    )

    @classmethod
    def get_db_error(cls) -> ErrorTrace:
        error = APISerializerErrorAppender.transform_invalid_api_key_error()
        return {'api_key': [{'type': error[0], 'message': error[1]}]}

class GetUserByIDFormatter:
    """Convenience class with DB error message."""

    @classmethod
    def get_db_error(cls, *, code: int) -> ErrorTrace:
        return {'user_id': [{'type': code, 'message': 'User with provided id doesn\'t exist'}]}


class CreateUserFormatter(BaseSerializerFormatter, BaseDBFormatter):
    class ErrorCode(IntEnum):
        NON_UNIQUE_EMAIL = 200

    @staticmethod
    def transform_email_error(error: PydanticError, _root: int) -> FormattedError | None:
        match error['type']:
            case 'missing':
                return FieldErrorCode.MISSING, 'Missing required field'
            case 'string_type':
                return FieldErrorCode.WRONG_TYPE, 'Email must be a string'
            case 'pattern_error':
                return FieldErrorCode.INVALID_PATTERN, 'Not a valid email address'

    @staticmethod
    def transform_password_error(error: PydanticError, _root: int) -> FormattedError | None:
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

    serializer_error_appender = BaseSerializerErrorAppender(
        email=append_serializer_field_error_factory(transform_email_error),
        password=append_serializer_field_error_factory(transform_password_error),
    )

    @staticmethod
    def transform_non_unique_email_error(*_) -> FormattedError:
        return CreateUserFormatter.ErrorCode.NON_UNIQUE_EMAIL, 'User with provided email already exists'

    db_error_appender = BaseDBErrorAppender({
        CreateUserErrorCode.NON_UNIQUE_EMAIL:
            append_db_field_error_factory('email', transformer=transform_non_unique_email_error),
    })


class LoginFormatter(BaseSerializerFormatter):
    serializer_error_appender = BaseSerializerErrorAppender(
        email=append_serializer_field_error_factory(CreateUserFormatter.transform_email_error),
        password=append_serializer_field_error_factory(CreateUserFormatter.transform_password_error),
        remember_me=append_serializer_field_error_factory(transform_bool_error_factory('Remember me')),
    )


class UpdateUserInfoFormatter(BaseSerializerFormatter):
    serializer_error_appender = RootSerializerErrorAppender(
        query=APISerializerErrorAppender(
            user_id=append_serializer_field_error_factory(transform_id_error_factory('User id')),
        ).append_error,
        body=BaseSerializerErrorAppender(
            name=append_serializer_field_error_factory(
                transform_str_error_factory('Name', min_length=1, max_length=50)),
            surname=append_serializer_field_error_factory(transform_str_error_factory('Surname', min_length=1,
                                                                                      max_length=50)),
            birthday=append_nested_model_error_factory(
                transformer=transform_nested_model_error_factory('Birthday'),
                model_error_appender=Date.append_serializer_error,
            ),
            city_id=append_serializer_field_error_factory(transform_id_error_factory('City id')),
        ).append_error,
    )


class UpdateUserAvatarFormatter(BaseSerializerFormatter, BaseDBFormatter):
    class ErrorCode(IntEnum):
        FILE_DOESNT_EXIST = 200

    serializer_error_appender = APISerializerErrorAppender(
        user_id=append_serializer_field_error_factory(transform_id_error_factory('User id')),
        avatar_filename=append_serializer_field_error_factory(transform_uuid_error_factory('Avatar filename')),
    )

    @staticmethod
    def transform_file_doesnt_exist_error(*_) -> FormattedError:
        return UpdateUserAvatarFormatter.ErrorCode.FILE_DOESNT_EXIST, 'File with provided name doesn\'t exist'

    db_error_appender = BaseDBErrorAppender({
        UpdateAvatarErrorCode.FILE_DOESNT_EXIST:
            append_db_field_error_factory(field_name='avatar_filename',
                                          transformer=transform_file_doesnt_exist_error),
    })


class GetCVByIDFormatter:
    """Convenience class with DB error message."""

    @classmethod
    def get_db_error(cls, *, code: int) -> ErrorTrace:
        return {'cv_id': [{'type': code, 'message': 'CV with provided id doesn\'t exist'}]}


class RenameCVFormatter(BaseSerializerFormatter):
    serializer_error_appender = BaseSerializerErrorAppender(
        cv_id=append_serializer_field_error_factory(transform_id_error_factory('CV id')),
        name=append_serializer_field_error_factory(transform_str_error_factory('CV name', min_length=1, max_length=50)),
    )

    @classmethod
    def get_insufficient_permissions_error(cls) -> ErrorTrace:
        return {'cv_id': [{'type': FieldErrorCode.INSUFFICIENT_PERMISSIONS,
                           'message': 'Can\'t rename CV with provided id'}]}

class DeleteCVFormatter(BaseSerializerFormatter):
    serializer_error_appender = APISerializerErrorAppender(
        cv_id=append_serializer_field_error_factory(transform_id_error_factory('CV id'))
    )

    @classmethod
    def get_insufficient_permissions_error(cls) -> ErrorTrace:
        return {'cv_id': [{'type': FieldErrorCode.INSUFFICIENT_PERMISSIONS,
                           'message': 'Can\'t delete CV with provided id'}]}
