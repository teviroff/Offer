from typing import Any, Self
from enum import StrEnum
import re

import mongoengine as mongo

from utils import *
import serializers.mod as ser


class SubmitMethodType(StrEnum):
    Noop = 'noop'
    YandexForms = 'yandex_forms'

class SubmitMethod(mongo.EmbeddedDocument):
    meta = {'allow_inheritance': True}

    type = mongo.EnumField(SubmitMethodType)

class NoopSubmitMethod(SubmitMethod):
    @classmethod
    def create(cls) -> Self:
        return NoopSubmitMethod(type=SubmitMethodType.Noop)

class YandexFormsSubmitMethod(SubmitMethod):
    url = mongo.URLField()

    @classmethod
    def create(cls, data: ser.OpportunityForm.YandexFormsSubmitMethod) -> Self:
        return YandexFormsSubmitMethod(type=SubmitMethodType.YandexForms, url=str(data.url))


class FieldType(StrEnum):
    String = 'string'
    Regex = 'regex'
    Choice = 'choice'

class FieldErrorCode(IntEnum):
    MISSING = 100
    EXTRA = 101
    WRONG_TYPE = 102
    LENGTH_NOT_IN_RANGE = 103
    INVALID_PATTERN = 104
    INVALID_CHOICE = 105

type FieldError = GenericError[FieldErrorCode, dict[str, Any]]

class OpportunityField(mongo.EmbeddedDocument):
    meta = {'allow_inheritance': True, 'abstract': True}

    label = mongo.StringField()
    type = mongo.EnumField(FieldType)
    is_required = mongo.BooleanField()

    def validate_input(self, field_name: str, input: Any) -> None | FieldError: ...

class StringField(OpportunityField):
    max_length = mongo.IntField()

    @classmethod
    def create(cls, data: ser.OpportunityForm.StringField) -> Self:
        return StringField(label=data.label, type=FieldType.String, is_required=data.is_required,
                           max_length=data.max_length)

    def validate_input(self, field_name: str, input: Any) -> None | FieldError:
        if not isinstance(input, str):
            return GenericError(
                error_code=FieldErrorCode.WRONG_TYPE,
                error_message='Field input must be a string',
                context={'field_name': field_name},
            )
        if self.max_length and len(input) > self.max_length:
            return GenericError(
                error_code=FieldErrorCode.LENGTH_NOT_IN_RANGE,
                error_message=f'Field input can contain at most {self.max_length} symbols',
                context={'field_name': field_name},
            )

    def to_dict(self) -> dict:
        return {
            'label': self.label,
            'is_requred': self.is_required,
            'max_length': self.max_length,
        }

class RegexField(StringField):
    regex = mongo.StringField()

    @classmethod
    def create(cls, data: ser.OpportunityForm.RegexField) -> Self:
        return RegexField(label=data.label, type=FieldType.Regex, is_required=data.is_required,
                          max_length=data.max_length, regex=data.regex)

    def validate_input(self, field_name: str, input: Any) -> None | FieldError:
        if error := super().validate_input(field_name, input):
            return error
        if not re.match(self.regex, input):
            return GenericError(
                error_code=FieldErrorCode.INVALID_PATTERN,
                error_message='Field input doesn\'t match expected pattern',
                context={'field_name': field_name},
            )

    def to_dict(self) -> dict:
        return {
            'label': self.label,
            'is_requred': self.is_required,
            'max_length': self.max_length,
            'regex': self.regex,
        }

class ChoiceField(OpportunityField):
    choices = mongo.ListField(mongo.StringField())

    @classmethod
    def create(cls, data: ser.OpportunityForm.ChoiceField) -> Self:
        return ChoiceField(label=data.label, type=FieldType.Choice, is_required=data.is_required,
                           choices=data.choices)

    def validate_input(self, field_name: str, input: Any) -> None | FieldError:
        if not isinstance(input, str):
            return GenericError(
                error_code=FieldErrorCode.WRONG_TYPE,
                error_message='Field input must be a string',
                context={'field_name': field_name},
            )
        if input not in self.choices:
            return GenericError(
                error_code=FieldErrorCode.INVALID_CHOICE,
                error_message='Field input must be one of provided choices',
                context={'field_name': field_name},
            )

    def to_dict(self) -> dict:
        return {
            'label': self.label,
            'is_requred': self.is_required,
            'choices': self.choices,
        }


class OpportunityForm(mongo.Document):
    id = mongo.IntField(primary_key=True)
    submit_method = mongo.EmbeddedDocumentField(SubmitMethod)
    fields = mongo.MapField(mongo.EmbeddedDocumentField(OpportunityField))

    @classmethod
    def create_submit(cls, data: ser.OpportunityForm.SubmitMethod) -> SubmitMethod:
        match data.type:
            case 'noop':
                return NoopSubmitMethod.create()
            case 'yandex_forms':
                return YandexFormsSubmitMethod.create(data)
        raise ValueError(f'Unhandled submit method: {data.type}')

    @classmethod
    def create_field(cls, data: ser.OpportunityForm.FormField) -> OpportunityField:
        match data.type:
            case 'string':
                return StringField.create(data)
            case 'regex':
                return RegexField.create(data)
            case 'choice':
                return ChoiceField.create(data)
        raise ValueError(f'Unhandled field type: {data.type}')

    @classmethod
    def create_fields(cls, fields: ser.OpportunityForm.FormFields) -> dict[str, OpportunityField]:
        return {name: cls.create_field(field) for name, field in fields.items()}

    @classmethod
    def create(cls, *, opportunity_id: int, submit: ser.OpportunityForm.SubmitMethod | None = None,
               fields: ser.OpportunityForm.FormFields) -> Self:
        self = OpportunityForm(id=opportunity_id, fields=cls.create_fields(fields))
        if submit is None:
            self.submit_method = NoopSubmitMethod.create()
        else:
            self.submit_method = cls.create_submit(submit)
        self.save()
        return self

    def update_submit_method(self, submit: ser.OpportunityForm.SubmitMethod) -> None:
        """Method for updating form submit method. Can't error in current implementation."""

        self.submit_method = self.create_submit(submit)
        self.save()

    def update_fields(self, fields: ser.OpportunityForm.FormFields) -> None:
        """Method for updating form fields. Can't error in current implementation."""

        self.fields = self.create_fields(fields)
        self.save()


class ResponseData(mongo.Document):
    id = mongo.IntField(primary_key=True)
    data = mongo.MapField(mongo.DynamicField())

    @classmethod
    def create(cls, *, response_id: int, form: OpportunityForm, data: ser.OpportunityResponse.CreateFields) \
            -> Self | list[FieldError]:
        response_data: dict[str, Any] = {}
        errors: list[FieldError] = []
        for name, value in data.data.items():
            field = form.fields.get(name)
            if field is None:
                errors.append(GenericError(
                    error_code=FieldErrorCode.EXTRA,
                    error_message='Unexpected field',
                    context={'field_name': name},
                ))
                continue
            error = field.validate_input(name, value)
            if error is None:
                response_data[name] = value
            else:
                errors.append(error)
        for name, field in form.fields.items():
            if name in data.data or not field.is_required:
                continue
            errors.append(GenericError(
                error_code=FieldErrorCode.MISSING,
                error_message='Missing required field',
                context={'field_name': name},
            ))
        if len(errors) > 0:
            return errors
        self = ResponseData(id=response_id, data=response_data)
        self.save()
        return self
