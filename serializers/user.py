from typing import Self
from datetime import datetime
import re

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_core import PydanticCustomError

class UserCredentials(BaseModel):
    model_config = { 'extra': 'ignore' }

    email: str
    password: str = Field(min_length=8)

    @field_validator('email')
    @classmethod
    def validate_email(cls, email: str) -> str:
        regex = re.compile(r'^((?!\.)[\w\-_.]*[^.])(@\w+)(\.\w+(\.\w+)?[^.\W])$')
        if not regex.match(email):
            raise PydanticCustomError('pattern_error',
                                      'Input should be a valid email address')
        return email

    @field_validator('password')
    @classmethod
    def validate_password(cls, password: str) -> str:
        regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\.-@$!%*?&])[A-Za-z\d\.-@$!%*?&]*$')
        if not regex.match(password):
            raise PydanticCustomError('pattern_error',
                                      'Input sould be a valid password')
        return password

class Date(BaseModel):
    model_config = { 'extra': 'ignore' }

    day: int = Field(ge=1, le=31, strict=True)
    month: int = Field(ge=1, le=12, strict=True)
    year: int = Field(ge=1900, strict=True)

    @model_validator(mode='after')
    def validate_date(self) -> Self:
        try:
            datetime(day=self.day, month=self.month, year=self.year)
        except ValueError:
            raise PydanticCustomError(
                'date_error', 'Invalid combination of year, month and day'
            )
        return self

class UserInfo(BaseModel):
    model_config = { 'extra': 'ignore' }

    user_id: int = Field(ge=1, strict=True)
    name: str | None = Field(default=None, max_length=50)
    surname: str | None = Field(default=None, max_length=50)
    birthday: Date | None = Field(default=None)
    # TODO: add Address and PhoneNumber pydantic models
    address: None = None
    phone_number: None = None
