from formatters.base import *
from utils import *
from models.user import CreateUserErrorCode

class POSTFormatter(BaseSerializerFormatter):
    class ErrorCode(IntEnum):
        NON_UNIQUE_EMAIL = 200

    @staticmethod
    def match_email_error(error_type: str) -> tuple[FieldErrorCode, str] | None:
        match error_type:
            case 'missing':
                return (FieldErrorCode.MISSING, 'Missing required field')
            case 'string_type':
                return (FieldErrorCode.WRONG_TYPE, 'Email must be a string')
            case 'pattern_error':
                return (FieldErrorCode.INVALID_PATTERN,
                        'Not a valid email address')
        return None

    @classmethod
    def append_email_error(cls, error: PydanticError, errors: Result) -> None:
        cls.append_serializer_field_error(
            error, errors,
            field_name='email', matcher=cls.match_email_error
        )

    @staticmethod
    def match_password_error(error_type: str) -> tuple[FieldErrorCode, str] | None:
        match error_type:
            case 'missing':
                return (FieldErrorCode.MISSING, 'Missing required field')
            case 'string_type':
                return (FieldErrorCode.WRONG_TYPE, 'Password must be a string')
            case 'string_too_short':
                return (FieldErrorCode.TOO_SHORT,
                        'Password must contain at least 8 characters')
            case 'pattern_error':
                return (FieldErrorCode.INVALID_PATTERN,
                        'Password must contain at least one lowercase letter, '
                        'one uppercase letter, one digit and one special character')
        return None

    @classmethod
    def append_password_error(cls, error: PydanticError, errors: Result) -> None:
        cls.append_serializer_field_error(
            error, errors,
            field_name='password', matcher=cls.match_password_error
        )

    @classmethod
    def append_serializer_error(cls, error: PydanticError, errors: Result,
                                root: int = 0) -> None:
        match error['loc'][root + 1]:
            case 'email':
                return cls.append_email_error(error, errors)
            case 'password':
                return cls.append_password_error(error, errors)
        raise ValueError(
            f'Unhandled serialization error at {error["loc"][root + 1]}'
        )

    @classmethod
    def format_db_error(cls, error: GenericError[CreateUserErrorCode]) -> Result:
        match error.error_code:
            case CreateUserErrorCode.NON_UNIQUE_EMAIL:
                return {
                    'email': [{
                        'type': cls.ErrorCode.NON_UNIQUE_EMAIL,
                        'message': 'User with provided email already exists'
                    }]
                }
        raise ValueError(f'Unhandled database error {error.error_code}')