from email.policy import strict, default
from typing import Any

from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
import re

import logging

from models.base import file_uri, FileURI

logger = logging.getLogger('serializers')

class OpportunityProvider(BaseModel):
    model_config = { 'extra': 'ignore' }

    name: str = Field(max_length=50)

class OpportunityTag(BaseModel):
    model_config = { 'extra': 'ignore' }

    name: str = Field(max_length=50)

class OpportunityGeoTag(BaseModel):
    model_config = { 'extra': 'ignore' }

    city_id: int = Field(ge=1, strict=True)

class OpportunityCard(BaseModel):
    model_config = { 'extra': 'ignore' }

    opportunity_id: int = Field(ge=1, strict=True)
    title: str = Field(max_length=30)
    sub_title: str | None = Field(max_length=30)

class Opportunity(BaseModel):
    model_config = { 'extra': 'ignore' }

    name: str = Field(max_length=50)
    provider_id: int = Field(ge=1, strict=True)
    description: str = Field(max_length=250)
