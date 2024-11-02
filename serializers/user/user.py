from typing import Annotated
from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
import re

class Create(BaseModel):
    model_config = { 'extra': 'ignore' }

    email: Annotated[str, Field(max_length=50)]
    password: Annotated[str, Field(min_length=8)]

    @field_validator('email')
    @classmethod
    def email_regex(cls, email: str) -> str:
        regex = re.compile(r'^((?!\.)[\w\-_.]*[^.])(@\w+)(\.\w+(\.\w+)?[^.\W])$')
        if not regex.match(email):
            raise PydanticCustomError('pattern_error',
                                      'Input should be a valid email address')
        return email

    @field_validator('password')
    @classmethod
    def password_regex(cls, password: str) -> str:
        regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\.-@$!%*?&])[A-Za-z\d\.-@$!%*?&]*$')
        if not regex.match(password):
            raise PydanticCustomError('pattern_error',
                                      'Input sould be a valid password')
        return password
