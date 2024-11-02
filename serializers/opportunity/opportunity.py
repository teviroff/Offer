from typing import Annotated
from pydantic import BaseModel, Field

class Create(BaseModel):
    model_config = { 'extra': 'ignore' }

    name: Annotated[str, Field(max_length=50)]
    provider_id: Annotated[int, Field(ge=1, strict=True)]
    description: Annotated[str, Field(max_length=250)]

class AddTags(BaseModel):
    model_config = { 'extra': 'ignore' }

    user_id: Annotated[int, Field(ge=1, strict=True)]
    tag_ids: list[Annotated[int, Field(ge=1, strict=True)]]

class AddGeoTags(BaseModel):
    model_config = { 'extra': 'ignore' }

    user_id: Annotated[int, Field(ge=1, strict=True)]
    geo_tag_ids: list[Annotated[int, Field(ge=1, strict=True)]]
