from serializers.base import *


class Create(BaseModel):
    model_config = {'extra': 'ignore'}

    api_key: API_KEY
    name: Annotated[str, Field(min_length=1, max_length=50)]
    provider_id: ID
    description: Annotated[str, Field(max_length=250)]


class Filter(BaseModel):
    model_config = {'extra': 'ignore'}

    api_key: OPTIONAL_API_KEY
    tag_ids: list[ID]
    geo_tag_ids: list[ID]


class AddTags(BaseModel):
    model_config = {'extra': 'ignore'}

    api_key: API_KEY
    opportunity_id: ID
    tag_ids: list[ID]


class AddGeoTags(BaseModel):
    model_config = {'extra': 'ignore'}

    api_key: API_KEY
    opportunity_id: ID
    geo_tag_ids: list[ID]
