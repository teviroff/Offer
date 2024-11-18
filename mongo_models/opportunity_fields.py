from typing import Self
from enum import StrEnum

import mongoengine as mongo

import serializers.mod as ser


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
    def create(cls, data: ser.OpportunityFields.StringField) -> Self:
        return StringField(label=data.label, type=FieldType.String, is_required=data.is_required,
                           max_length=data.max_length)

class RegexField(StringField):
    regex = mongo.StringField()

    @classmethod
    def create(cls, data: ser.OpportunityFields.RegexField) -> Self:
        return RegexField(label=data.label, type=FieldType.Regex, is_required=data.is_required,
                          max_length=data.max_length, regex=data.regex)

class ChoiceField(OpportunityField):
    choices = mongo.ListField(mongo.StringField())

    @classmethod
    def create(cls, data: ser.OpportunityFields.ChoiceField) -> Self:
        return ChoiceField(label=data.label, type=FieldType.Choice, is_required=data.is_required,
                           choices=data.choices)


class OpportunityFields(mongo.Document):
    form_link = mongo.StringField()
    fields = mongo.EmbeddedDocumentListField(OpportunityField)

    @classmethod
    def create_field(cls, data: ser.OpportunityFields.FormField) -> OpportunityField:
        match data.type:
            case 'string':
                return StringField.create(data)
            case 'regex':
                return RegexField.create(data)
            case 'choice':
                return ChoiceField.create(data)
        raise ValueError(f'Unhandled field type: {data.type}')

    @classmethod
    def create(cls, request: ser.OpportunityFields.FormFields):
        self = OpportunityFields(form_link=str(request.form_link),
                                 fields=[cls.create_field(field) for field in request.fields]).save()
        return self
