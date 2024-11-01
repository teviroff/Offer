from typing import Any, Iterable

from formatters.base import *
from models.auxillary.phone_number import CreatePhoneNumberErrorCode
from utils import GenericError

from models.opportunity.opportunity import (
    CreateOpportunityError, FilterOpportunityError,
    AddOpportunityTagError, CreateOpportunityTagError,
    CreateOpportunityGeoTagError, CreateOpportunityErrorCode
)

class Opportunity(BaseFormatter):
    serializer_name_errors = {
        'missing': (FieldErrorCode.MISSING, 'Missing required field'),
        'string_type': (FieldErrorCode.WRONG_TYPE, 'Name of opportunity must be string'),
        'string_too_long': (FieldErrorCode.TOO_LONG, 'Name of opportunity must contain maximum 50 characters'),
    }
    serializer_provider_id_errors = {
        'missing': (FieldErrorCode.MISSING, 'Missing required field'),
        'int_type': (FieldErrorCode.WRONG_TYPE, 'Provider id must be integer'),
    }
    serializer_description_errors = {
        'missing': (FieldErrorCode.MISSING, 'Missing required field'),
        'string_type': (FieldErrorCode.WRONG_TYPE, 'Description must be string'),
        'string_too_long': (FieldErrorCode.TOO_LONG, 'Description must contain maximum 128 characters'),
    }
    serializer_required_data_errors = {
        'missing': (FieldErrorCode.MISSING, 'Missing required field'),
        'string_type': (FieldErrorCode.WRONG_TYPE, 'Required data must be string'),
        'string_too_long': (FieldErrorCode.TOO_LONG, 'Requires data must contain maximum 128 characters'),
    }

    @classmethod
    def add_error(cls, error: PydanticError, errors: Result, root: int = 0) -> None:
        match error['loc'][root + 1]:
            case 'name':
                e = cls.serializer_name_errors[error['type']]
                errors['name'] = [{'type': e[0], 'message': e[1]}]
            case 'provider_id':
                e = cls.serializer_provider_id_errors[error['type']]
                errors['provider_id'] = [{'type': e[0], 'message': e[1]}]
            case 'description':
                e = cls.serializer_description_errors[error['type']]
                errors['description'] = [{'type': e[0], 'message': e[1]}]
            case 'required_data':
                e = cls.serializer_required_data_errors[error['type']]
                errors['required_data'] = [{'type': e[0], 'message': e[1]}]

    @classmethod
    def format_db_error(cls, raw_error: GenericError[CreateOpportunityErrorCode]) -> Result:
        # TODO: finish
        match raw_error.error_code:
            case CreateOpportunityErrorCode.INVALID_PROVIDER_ID:
                return {
                    'stage': 1,
                    'provider': [
                        {
                            'type': CreateOpportunityErrorCode.INVALID_PROVIDER_ID,
                            'message': 'Provider with provided id doesn\'t exist'
                        }
                    ]
                }
