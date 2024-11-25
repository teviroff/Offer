from copy import copy

from formatters.base import *


class FieldSerializerErrorAppender(BaseSerializerErrorAppender):
    def __init__(self, **kwargs: SerializerErrorAppender):
        super().__init__(**kwargs)
        self.label = append_serializer_field_error_factory(transform_str_error_factory('Label'))
        self.is_required = append_serializer_field_error_factory(transform_bool_error_factory('Is required'))


class StringFieldFormatter(BaseSerializerFormatter):
    serializer_error_appender = FieldSerializerErrorAppender(
        max_length=append_serializer_field_error_factory(transform_int_error_factory('Max length', ge=1))
    )

class RegexFieldFormatter(StringFieldFormatter):
    @staticmethod
    def transform_regex_error(error: PydanticError, _root: int) -> FormattedError | None:
        match error['type']:
            case 'missing':
                return FieldErrorCode.MISSING, 'Missing required field'
            case 'string_type':
                return FieldErrorCode.WRONG_TYPE, 'Regex must be a string'
            case 'pattern_error':
                return FieldErrorCode.INVALID_PATTERN, 'Regex must be a valid regular expression'

    serializer_error_appender = copy(StringFieldFormatter.serializer_error_appender) \
        .add_field_error_appender('regex', append_serializer_field_error_factory(transform_regex_error))

class ChoiceFieldFormatter(BaseSerializerFormatter):
    serializer_error_appender = FieldSerializerErrorAppender(
        choices=append_serializer_list_error_factory(
            transformer=transform_list_error_factory('Choices', min_length=1),
            element_error_appender=append_serializer_field_error_factory(transform_str_error_factory('Choice name')),
        )
    )


class FormFieldsFormatter(BaseSerializerFormatter):
    serializer_error_appender = BaseSerializerErrorAppender(
        form_link=append_serializer_field_error_factory(transform_http_url_error_factory('Form link')),
        fields=append_serializer_list_error_factory(
            transformer=transform_list_error_factory('Form fields', min_length=1),
            element_error_appender=append_tagged_union_error(transform_tagged_union_error_factory('Form field'))
                .add_variant_error_appender('string', StringFieldFormatter.append_serializer_error)
                .add_variant_error_appender('regex', RegexFieldFormatter.append_serializer_error)
                .add_variant_error_appender('choice', ChoiceFieldFormatter.append_serializer_error),
        )
    )
