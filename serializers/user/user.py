from serializers.base import *
from pydantic import field_validator
from pydantic_core import PydanticCustomError
from ipaddress import IPv4Address
import re


class Credentials(BaseModel):
    """Model used for registration/login DB API methods."""

    model_config = {'extra': 'ignore'}

    email: Annotated[str, Field(max_length=50)]
    password: Annotated[str, Field(min_length=8)]

    @field_validator('email')
    @classmethod
    def email_regex(cls, email: str) -> str:
        regex = re.compile(r'^((?!\.)[\w\-_.]*[^.])(@\w+)(\.\w+(\.\w+)?[^.\W])$')
        if not regex.match(email):
            raise PydanticCustomError('pattern_error', 'Input should be a valid email address')
        return email

    @field_validator('password')
    @classmethod
    def password_regex(cls, password: str) -> str:
        regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[.\-@$!%*?&])[A-Za-z\d.-@$!%*?&]*$')
        if not regex.match(password):
            raise PydanticCustomError('pattern_error', 'Input should be a valid password')
        return password


class LoginFields(Credentials):
    """Model used in login handler. Should be transformed into 'Login' and passed to middleware."""

    remember_me: Annotated[Annotated[bool, Field(strict=True)], Field(default=False)]

class Login(LoginFields):
    """Module with all required information about login attempt. Used only by middleware."""

    ip: IPv4Address
    port: Annotated[int, Field(strict=True, ge=0, lt=65536)]


class QueryParameters(BaseModel):
    model_config = {'extra': 'ignore'}

    api_key: API_KEY
    user_id: ID
