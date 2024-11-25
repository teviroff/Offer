from typing import Self
from enum import StrEnum

import mongoengine as mongo

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

# TODO: integrate field error messages in here
class OpportunityField(mongo.EmbeddedDocument):
    meta = {'allow_inheritance': True}

    label = mongo.StringField()
    type = mongo.EnumField(FieldType)
    is_required = mongo.BooleanField()

class StringField(OpportunityField):
    max_length = mongo.IntField()

    @classmethod
    def create(cls, data: ser.OpportunityForm.StringField) -> Self:
        return StringField(label=data.label, type=FieldType.String, is_required=data.is_required,
                           max_length=data.max_length)

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
