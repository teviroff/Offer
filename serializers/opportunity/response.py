from datetime import datetime
from email.policy import strict, default
from typing import Any

from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
import re

import logging

from models.base import file_uri, FileURI

logger = logging.getLogger('serializers')

class ResponseStatus(BaseModel):
    model_config = { 'extra': 'ignore' }

    response_id: int = Field(ge=1, strict=True)
    status: str = Field(max_length=50)
    description: str = Field(max_length=200)
    timestamp: datetime = Field(default_factory=datetime.now)
