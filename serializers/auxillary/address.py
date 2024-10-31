from typing import Any
from pydantic import BaseModel, field_validator
from pydantic_core import PydanticCustomError
import re

import logging

logger = logging.getLogger('serializers')

class Address(BaseModel):
    country: str
    city: str
    street: str
    house: int

    @field_validator('country', mode='before')
    @classmethod
    def validate_country(cls, country: Any) -> str:
        if not isinstance(country, str):
            # log
            raise PydanticCustomError(
                'field_type_error',
                'Value of \'country\' field must be a string'
            )
        # ...
        
