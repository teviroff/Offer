from pydantic import HttpUrl, field_validator
from pydantic_core import PydanticCustomError

from serializers.base import *
import serializers.opportunity.fields as fields


class CreateFields(BaseModel):
    model_config = {'extra': 'ignore'}

    name: Annotated[str, Field(min_length=1, max_length=50)]
    link: Annotated[HttpUrl | None, Field(default=None)]
    provider_id: ID
    fields: Annotated[fields.FormFields | None, Field(default=None)]

    @field_validator('link')
    @classmethod
    def validate_link_length(cls, link: str) -> str:
        if len(link) > 120:
            raise PydanticCustomError('string_too_long', 'Opportunity URL can contain at most 120 characters')
        return link

class Create(CreateFields):
    api_key: API_KEY


class Filter(BaseModel):
    model_config = {'extra': 'ignore'}

    api_key: OPTIONAL_API_KEY
    tag_ids: list[ID]
    geo_tag_ids: list[ID]


class AddTagsFields(BaseModel):
    model_config = {'extra': 'ignore'}

    opportunity_id: ID
    tag_ids: list[ID]

class AddTags(AddTagsFields):
    api_key: API_KEY


class AddGeoTagsFields(BaseModel):
    model_config = {'extra': 'ignore'}

    opportunity_id: ID
    geo_tag_ids: list[ID]

class AddGeoTags(AddGeoTagsFields):
    api_key: API_KEY
