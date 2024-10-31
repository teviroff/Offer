from typing import Any, Iterable

from formatters.base import *
from models.auxillary.phone_number import CreatePhoneNumberError, CreatePhoneNumberErrorCode

from models.opportunity.opportunity import (
    CreateOpportunityError, FilterOpportunityError,
    AddOpportunityTagError, CreateOpportunityTagError,
    CreateOpportunityGeoTagError
)

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