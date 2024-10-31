from typing import Any, Iterable

from formatters.base import *

from models.user import (
    CreateUserError, CreateUserErrorCode,
    UpdateUserInfoError, UpdateUserInfoErrorCode,
)

type PydanticError = dict[str, Any]
type Result = dict[str, int | list[dict[str, int | str]]]

class User:
    serializer_email_errors = {
        'missing': (FieldErrorCode.MISSING, 'Missing required field'),
        'string_type': (FieldErrorCode.WRONG_TYPE, 'Email must be a string'),
        'pattern_error': (FieldErrorCode.INVALID_PATTERN,
                          'Not a valid email address'),
    }

    serializer_password_errors = {
        'missing': (FieldErrorCode.MISSING, 'Missing required field'),
        'string_type': (FieldErrorCode.WRONG_TYPE, 'Password must be a string'),
        'string_too_short': (FieldErrorCode.TOO_SHORT,
                             'Password must contain at least 8 characters'),
        'pattern_error': (FieldErrorCode.INVALID_PATTERN,
                          'Password must contain at least one lowercase letter, '
                          'one uppercase letter, one digit and one special character'),
    }

    @classmethod
    def format_serializer_errors(cls, raw_errors: Iterable[PydanticError]) -> Result:
        errors: Result = { 'stage': 0, 'email': [], 'password': [] }
        for error in raw_errors:
            match error['loc'][-1]:
                case 'email':
                    err = cls.serializer_email_errors[error['type']]
                    errors['email'].append({
                        'type': err[0],
                        'message': err[1]
                    })
                case 'password':
                    err = cls.serializer_password_errors[error['type']]
                    errors['password'].append({
                        'type': err[0],
                        'message': err[1]
                    })
        if len(errors['email']) == 0:
            del errors['email']
        elif len(errors['password']) == 0:
            del errors['password']
        return errors

    @classmethod
    def format_db_error(cls, raw_error: CreateUserError) -> Result:
        match raw_error.error_code:
            case CreateUserErrorCode.NON_UNIQUE_EMAIL:
                return {
                    'stage': 1,
                    'email': [
                        {
                            'type': CreateUserErrorCode.NON_UNIQUE_EMAIL,
                            'message': 'User with provided email already exists'
                        }
                    ]
                }
        raise ValueError(f'Unhandled database error {raw_error.error_code}')

class Date:
    serializer_day_errors = {
        'missing': (FieldErrorCode.MISSING, 'Missing required field'),
        'int_type': (FieldErrorCode.WRONG_TYPE, 'Day must be an int'),
        'greater_than_equal': (FieldErrorCode.NOT_IN_RANGE,
                               'Day must be in range from 1 to 31'),
        'less_than_equal': (FieldErrorCode.NOT_IN_RANGE,
                            'Day must be in range from 1 to 31'),
    }

    serializer_month_errors = {
        'missing': (FieldErrorCode.MISSING, 'Missing required field'),
        'int_type': (FieldErrorCode.WRONG_TYPE, 'Month must be an int'),
        'greater_than_equal': (FieldErrorCode.NOT_IN_RANGE,
                               'Month must be in range from 1 to 12'),
        'less_than_equal': (FieldErrorCode.NOT_IN_RANGE,
                            'Month must be in range from 1 to 12'),
    }

    serializer_year_errors = {
        'missing': (FieldErrorCode.MISSING, 'Missing required field'),
        'int_type': (FieldErrorCode.WRONG_TYPE, 'Year must be an int'),
        'greater_than_equal': (FieldErrorCode.NOT_IN_RANGE,
                               'Year must be greater than or equal to 1900')
    }

    @classmethod
    def add_error(cls, error: PydanticError, errors: Result,
                  root: int = 0) -> None:
        if len(error['loc']) == root + 1:
            # occurs only if all inner fields are valid, so assign directly
            errors = {
                'type': 0,
                'message': 'Invalid combination of year, month and day'
            }
        match error['loc'][root + 1]:
            case 'day':
                e = cls.serializer_day_errors[error['type']]
                # errors are mutually exclusive, so assign directly
                errors['day'] = [{ 'type': e[0], 'message': e[1] }]
            case 'month':
                e = cls.serializer_month_errors[error['type']]
                # errors are mutually exclusive, so assign directly
                errors['month'] = [{ 'type': e[0], 'message': e[1] }]
            case 'year':
                e = cls.serializer_year_errors[error['type']]
                # errors are mutually exclusive, so assign directly
                errors['year'] = [{ 'type': e[0], 'message': e[1] }]

    @classmethod
    def format_serializer_errors(cls, raw_errors: Iterable[PydanticError],
                                 root: int = 0) -> Result:
        errors: Result = { 'stage': 0 } if root == 0 else {}
        for error in raw_errors:
            cls.add_error(error, errors, root)
        return errors

class UserInfo:
    serializer_user_id_errors = {
        'missing': (FieldErrorCode.MISSING, 'Missing required field'),
        'int_type': (FieldErrorCode.WRONG_TYPE, 'User id must be an int'),
        'greater_than_equal': (FieldErrorCode.NOT_IN_RANGE,
                               'User id must be greater than or equal to 1'),
    }

    serializer_name_errors = {
        'string_type': (FieldErrorCode.WRONG_TYPE, 'Name must be a string'),
        'string_too_long': (FieldErrorCode.TOO_LONG,
                            'Name must contain at most 50 characters'),
    }

    serializer_surname_errors = {
        'string_type': (FieldErrorCode.WRONG_TYPE, 'Surname must be a string'),
        'string_too_long': (FieldErrorCode.TOO_LONG,
                            'Surname must contain at most 50 characters'),
    }

    serializer_birthday_errors = {
        'model_attributes_type': (FieldErrorCode.WRONG_TYPE,
                                  'Birthday must be a dictionary'),
    }

    @classmethod
    def add_error(cls, error: PydanticError, errors: Result,
                  root: int = 0) -> None:
        match error['loc'][root + 1]:
            case 'user_id':
                e = cls.serializer_user_id_errors[error['type']]
                # errors are mutually exclusive, so assign directly
                errors['user_id'] = [{ 'type': e[0], 'message': e[1] }]
            case 'name':
                e = cls.serializer_name_errors[error['type']]
                # errors are mutually exclusive, so assign directly
                errors['name'] = [{ 'type': e[0], 'message': e[1] }]
            case 'surname':
                e = cls.serializer_surname_errors[error['type']]
                # errors are mutually exclusive, so assign directly
                errors['surname'] = [{ 'type': e[0], 'message': e[1] }]
            case 'birthday':
                if error['type'] in cls.serializer_birthday_errors:
                    e = cls.serializer_birthday_errors[error['type']]
                    # excludes possibility for inner errors
                    errors['birthday'] = { 'type': e[0], 'message': e[1] }
                else:
                    if 'birthday' not in errors:
                        errors['birthday'] = {}
                    Date.add_error(error, errors['birthday'], root + 1)

    @classmethod
    def format_serializer_errors(cls, raw_errors: Iterable[PydanticError],
                                 root: int = 0) -> Result:
        errors: Result = { 'stage': 0 } if root == 0 else {}
        for error in raw_errors:
            cls.add_error(error, errors, root)
        return errors

    @classmethod
    def format_db_error(cls, raw_error: UpdateUserInfoError) -> Result:
        match raw_error.error_code:
            case UpdateUserInfoErrorCode.INVALID_USER_ID:
                return {
                    'stage': 1,
                    'email': [
                        {
                            'type': UpdateUserInfoErrorCode.INVALID_USER_ID,
                            'message': 'User with provided id doesn\'t exist'
                        }
                    ]
                }
        raise ValueError(f'Unhandled database error {raw_error.error_code}')
