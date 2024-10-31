from dataclasses import Field
from email.policy import strict, default
from typing import Any

from attr.validators import max_len
from pydantic import BaseModel, field_validator
from pydantic_core import PydanticCustomError
import re

import logging

from models.base import file_uri, FileURI

logger = logging.getLogger('serializers')

class OpportunityProvider(BaseModel):
    model_config = { 'extra': 'ignore' }

    id: int = Field(ge=1, strict=True)
    name: str = Field(max_length=50)
    logo: file_uri = Field(default=None)

class OpportunityTag(BaseModel):
    model_config = { 'extra': 'ignore' }

    name: str = Field(max_length=50)

class OpportunityGeoTag(BaseModel):
    model_config = { 'extra': 'ignore' }

    city_id: int = Field(ge=1, strict=True)

class OpportunityCard(BaseModel):
    model_config = { 'extra': 'ignore' }

    opportunity_id: int = Field(ge=1, strict=True)

class Opportunity(BaseModel):
    model_config = { 'extra': 'ignore' }

    name: str = Field(default=None, max_length=50)
    provider_id: int = Field(ge=1, strict=True)
    description: file_uri = Field(default=None)
    required_data: file_uri = Field(default=None)
