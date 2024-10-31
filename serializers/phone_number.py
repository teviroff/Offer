from dataclasses import Field
from typing import Any

from attr.validators import max_len
from pydantic import BaseModel, field_validator
from pydantic_core import PydanticCustomError
import re

import logging

logger = logging.getLogger('serializers')

class PhoneNumber(BaseModel):
    model_config = { 'extra': 'ignore' }
    country_id: int = Field(strict=True, ge=1)
    sub_number: str = Field(max_length=12)


