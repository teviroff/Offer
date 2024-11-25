from typing import Self
from enum import StrEnum

import mongoengine as mongo

import serializers.mod as ser


class SubmitMethodType(StrEnum):
    Noop = 'noop'

class SubmitMethod(mongo.EmbeddedDocument):
    meta = {'allow_inheritance': True}

    type: mongo.EnumField(SubmitMethodType)

class NoopSubmitMethod(SubmitMethod):
    @classmethod
    def create(cls) -> Self:
        return NoopSubmitMethod(type=SubmitMethodType.Noop)


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
    submit = mongo.EmbeddedDocument(SubmitMethod)
    fields = mongo.EmbeddedDocumentListField(OpportunityField)

    @classmethod
    def create_submit(cls, data: ser.OpportunityForm.SubmitMethod) -> SubmitMethod:
        match data.type:
            case 'noop':
                return NoopSubmitMethod.create()
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
    def create_fields(cls, fields: ser.OpportunityForm.FormFields) -> list[OpportunityField]:
        return [cls.create_field(field) for field in fields]

    @classmethod
    def create(cls, *, submit: ser.OpportunityForm.SubmitMethod | None = None, fields: ser.OpportunityForm.FormFields):
        self = OpportunityForm(fields=cls.create_fields(fields))
        if submit is None:
            submit = NoopSubmitMethod.create()
        else:
            submit = cls.create_submit(submit)
        self.save()
        return self
