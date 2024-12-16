from typing import Self
from datetime import datetime

from serializers.base import *
from pydantic import model_validator
from pydantic_core import PydanticCustomError


class Date(BaseModel):
    model_config = {'extra': 'ignore'}

    day: Annotated[int, Field(ge=1, le=31, strict=True)]
    month: Annotated[int, Field(ge=1, le=12, strict=True)]
    year: Annotated[int, Field(ge=1900, strict=True)]

    @model_validator(mode='after')
    def validate_date(self) -> Self:
        try:
            datetime(day=self.day, month=self.month, year=self.year)
        except ValueError:
            raise PydanticCustomError('date_error', 'Invalid combination of year, month and day')
        return self


class PhoneNumber(BaseModel):
    model_config = {'extra': 'ignore'}

    country_id: ID
    sub_number: Annotated[str, Field(max_length=12, pattern=r'\d+')]


class Country(BaseModel):
    model_config = {'extra': 'ignore'}

    name: Annotated[str, Field(min_length=1, max_length=50)]
    phone_code: Annotated[int, Field(ge=1, le=999)]


class City(BaseModel):
    model_config = {'extra': 'ignore'}

    name: Annotated[str, Field(min_length=1, max_length=50)]

class CreateCityQueryParameters(QueryParameters):
    country_id: ID
