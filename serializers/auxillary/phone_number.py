from typing import Any
from pydantic import BaseModel, field_validator
from pydantic_core import PydanticCustomError
import re

import logging

logger = logging.getLogger('serializers')

class PhoneNumber(BaseModel):
    model_config = { 'extra': 'forbid' }

    country_id: int
    sub_number: str

    @field_validator('country_id', mode='before')
    @classmethod
    def validate_country_id(cls, country_id: Any) -> int:
        if not isinstance(country_id, int):
            # log
            raise PydanticCustomError(
                'field_type_error',
                'Value of \'country_id\' field must be an int'
            )
        if country_id < 1:
            # log
            raise PydanticCustomError(
                'field_value_error',
                'Value of \'country_id\' field must be >= 1'
            )
        return country_id

    @field_validator('number', mode='before')
    @classmethod
    def validate_number(cls, number: Any) -> str:
        if not isinstance(number, str):
            # log
            raise PydanticCustomError(
                'field_type_error',
                'Value of \'sub_number\' field must be a string'
            )
        if len(number) > 12:
            # log
            raise PydanticCustomError(
                'field_length_error',
                'Subscriber number can contain at most 12 digits'
            )
        regex = re.compile(r'^\d*$')
        if not regex.match(number):
            # log
            raise PydanticCustomError(
                'field_pattern_error',
                '\'sub_number\' can contain only digits'
            )
        return number
