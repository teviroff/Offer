from typing import Any, Iterable

from formatters.base import *
from models.auxillary.phone_number import CreatePhoneNumberErrorCode
from utils import GenericError

from models.opportunity.response import (
    CreateResponseStatusErrorCode
)

class ResponseStatus(BaseFormatter):
    serializer_response_id_errors = {
        'missing': (FieldErrorCode.MISSING, 'Missing required field'),
        'int_type': (FieldErrorCode.WRONG_TYPE, 'Response id must be integer'),
    }
    serializer_status_errors = {
        'missing': (FieldErrorCode.MISSING, 'Missing required field'),
        'string_type': (FieldErrorCode.WRONG_TYPE, 'Status must be string'),
        'string_too_long': (FieldErrorCode.TOO_LONG, 'Status must contain maximum 50 characters'),
    }
    serializer_description_errors = {
        'missing': (FieldErrorCode.MISSING, 'Missing required field'),
        'string_type': (FieldErrorCode.WRONG_TYPE, 'Description must be string'),
        'string_too_long': (FieldErrorCode.TOO_LONG, 'Description must contain maximum 200 characters'),
    }
    serializer_timestamp_errors = {
        'missing': (FieldErrorCode.MISSING, 'Missing required field'),
        # 'date_type': (FieldErrorCode.WRONG_TYPE, 'Description must be string'),
    }

    @classmethod
    def add_error(cls, error: PydanticError, errors: Result, root: int = 0) -> None:
        match error['loc'][root + 1]:
            case 'response_id':
                e = cls.serializer_response_id_errors[error['type']]
                errors['name'] = [{'type': e[0], 'message': e[1]}]
            case 'status':
                e = cls.serializer_status_errors[error['type']]
                errors['status'] = [{'type': e[0], 'message': e[1]}]
            case 'description':
                e = cls.serializer_description_errors[error['type']]
                errors['description'] = [{'type': e[0], 'message': e[1]}]
            case 'timestamp':
                e = cls.serializer_timestamp_errors[error['type']]
                errors['timestamp'] = [{'type': e[0], 'message': e[1]}]

    @classmethod
    def format_db_error(cls, raw_error: GenericError[CreateResponseStatusErrorCode]) -> Result:
        # TODO: finish
        match raw_error.error_code:
            case CreateResponseStatusErrorCode.INVALID_RESPONSE_ID:
                return {
                    'stage': 1,
                    'response': [
                        {
                            'type': raw_error.error_code,
                            'message': 'Response with provided id doesn\'t exist'
                        }
                    ]
                }

