from typing import Any, Iterable

from formatters.base import *
from models.auxillary.phone_number import CreatePhoneNumberErrorCode
from utils import GenericError

from models.opportunity.opportunity import (
    CreateOpportunityError, FilterOpportunityError,
    AddOpportunityTagError, CreateOpportunityTagError,
    CreateOpportunityGeoTagError, CreateOpportunityErrorCode
)

type PydanticError = dict[str, Any]
type Result = dict[str, int | dict[str, Result] | list[dict[str, Result]]]

class Opportunity:
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
    def format_serializer_errors(cls, raw_errors: Iterable[PydanticError],
                                 root: int = 0) -> Result:
        errors: Result = {'stage': 0} if root == 0 else {}
        for error in raw_errors:
            cls.add_error(error, errors)
        return errors

    @classmethod
    def format_db_error(cls, raw_errors: GenericError[CreateOpportunityErrorCode]) -> Result:
        # TODO: finish
        match raw_errors.error_code:
            case CreateOpportunityErrorCode:
                return {
                    'stage': 1,
                    'opportunity': [
                        {
                            'type': CreatePhoneNumberErrorCode.INVALID_COUNTRY_ID,
                            'message': 'Country with provided id doesn\'t exist'
                        }
                    ]
                }
