from pydantic import HttpUrl, field_validator
from pydantic_core import PydanticCustomError

from serializers.base import *
import serializers.opportunity.form as form


class Create(BaseModel):
    model_config = {'extra': 'ignore'}

    name: Annotated[str, Field(min_length=1, max_length=50)]
    link: Annotated[HttpUrl | None, Field(default=None)]
    provider_id: ID

    @field_validator('link')
    @classmethod
    def validate_link_length(cls, link: str) -> str:
        if len(link) > 120:
            raise PydanticCustomError('string_too_long', 'Opportunity URL can contain at most 120 characters')
        return link

class QueryParameters(BaseModel):
    model_config = {'extra': 'ignore'}

    api_key: API_KEY
    opportunity_id: ID


class Filter(BaseModel):
    model_config = {'extra': 'ignore'}

    api_key: OPTIONAL_API_KEY
    tag_ids: list[ID]
    geo_tag_ids: list[ID]


class AddTags(BaseModel):
    model_config = {'extra': 'ignore'}

    tag_ids: list[ID]

class AddTagsQueryParameters(BaseModel):
    model_config = {'extra': 'ignore'}

    api_key: API_KEY
    opportunity_id: ID


class AddGeoTagsFields(BaseModel):
    model_config = {'extra': 'ignore'}

    geo_tag_ids: list[ID]

class AddGeoTags(AddGeoTagsFields):
    api_key: API_KEY
    opportunity_id: ID


class UpdateFormSubmit(BaseModel):
    model_config = {'extra': 'ignore'}

    submit: form.SubmitMethod


class UpdateFormFields(BaseModel):
    model_config = {'extra': 'ignore'}

    fields: form.FormFields
