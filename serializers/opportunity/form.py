from typing import Literal
import re

from pydantic import field_validator
from pydantic_core import PydanticCustomError

from serializers.base import *


class SubmitMethodBase(BaseModel):
    model_config = {'extra': 'ignore'}

class NoopSubmitMethod(SubmitMethodBase):
    type: Literal['noop']

type SubmitMethod = Annotated[NoopSubmitMethod, Field(discriminator='type')]


class FormFieldBase(BaseModel):
    model_config = {'extra': 'ignore'}

    label: str
    is_required: Annotated[bool, Field(strict=True)]

class StringField(FormFieldBase):
    type: Literal['string']
    max_length: Annotated[Annotated[int, Field(strict=True, ge=1)] | None, Field(default=None)]

class RegexField(StringField):
    type: Literal['regex']
    regex: str

    @field_validator('regex')
    @classmethod
    def validate_regex(cls, regex: str) -> str:
        try:
            re.compile(regex)
        except re.PatternError:
            raise PydanticCustomError('pattern_error', 'Input should be a valid regular expression')
        return regex

class ChoiceField(FormFieldBase):
    type: Literal['choice']
    choices: Annotated[list[str], Field(min_length=1)]

type FormField = Annotated[StringField | RegexField | ChoiceField, Field(discriminator='type')]
type FormFields = Annotated[list[FormField], Field(min_length=1)]
