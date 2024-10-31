"""Models in this module are not accessable through the API.
   They are defined for pure convenience, when adding them by hand."""

from pydantic import BaseModel, Field

class Country(BaseModel):
    model_config = { 'extra': 'forbid' }

    name: str = Field(min_length=1, max_length=50)
    phone_code: int = Field(ge=1, lt=1000)

class City(BaseModel):
    model_config = { 'extra': 'forbid' }

    country_id: int = Field(ge=1, strict=True)
    name: str = Field(min_length=1, max_length=50)
