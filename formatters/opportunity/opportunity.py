from formatters.base import *
from utils import *
from models.opportunity.opportunity import (
    CreateOpportunityErrorCode, AddOpportunityTagErrorCode,
    AddOpportunityGeoTagErrorCode,
)


class GetOpportunityByIDFormatter:
    """Convenience class with DB error message."""

    @classmethod
    def get_db_error(cls, *, code: int) -> ErrorTrace:
        return {'opportunity_id': [{'type': code, 'message': 'Opportunity with provided id doesn\'t exist'}]}


class CreateOpportunityFormatter(BaseSerializerFormatter, BaseDBFormatter):
    class ErrorCode(IntEnum):
        INVALID_PROVIDER_ID = 200

    serializer_error_appender = RootSerializerErrorAppender(
        query=APISerializerErrorAppender().append_error,
        body=BaseSerializerErrorAppender(
            name=append_serializer_field_error_factory(transform_str_error_factory(
                'Opportunity name', min_length=1, max_length=50)),
            link=append_serializer_field_error_factory(transform_http_url_error_factory(
                'Opportunity link', max_length=120)),
            provider_id=append_serializer_field_error_factory(transform_id_error_factory('Opportunity provider id')),
        ).append_error,
    )

    @staticmethod
    def transform_invalid_provider_id_error(*_) -> FormattedError:
        return CreateOpportunityFormatter.ErrorCode.INVALID_PROVIDER_ID, \
               'Opportunity provider with given id doesn\'t exist'

    db_error_appender = BaseDBErrorAppender({
        CreateOpportunityErrorCode.INVALID_PROVIDER_ID:
            append_db_field_error_factory('provider_id', transformer=transform_invalid_provider_id_error),
    })


class FilterOpportunitiesFormatter(BaseDBFormatter):
    class ErrorCode(IntEnum):
        INVALID_PROVIDER_ID = 200
        INVALID_TAG_ID = 201
        INVALID_GEO_TAG_ID = 202

    @staticmethod
    def append_invalid_provider_id_error(error: GenericError[ErrorCode, int], errors: ErrorTrace, _) -> None:
        if 'provider_ids' not in errors:
            errors['provider_ids'] = {}
        tag_index = str(error.context)
        if tag_index not in errors['provider_ids']:
            errors['provider_ids'][tag_index] = []
        errors['provider_ids'][tag_index].append({'type': error.error_code, 'message': error.error_message})

    @staticmethod
    def append_invalid_tag_id_error(error: GenericError[ErrorCode, int], errors: ErrorTrace, _) -> None:
        if 'tag_ids' not in errors:
            errors['tag_ids'] = {}
        tag_index = str(error.context)
        if tag_index not in errors['tag_ids']:
            errors['tag_ids'][tag_index] = []
        errors['tag_ids'][tag_index].append({'type': error.error_code, 'message': error.error_message})

    @staticmethod
    def append_invalid_geo_tag_id_error(error: GenericError[ErrorCode, int], errors: ErrorTrace, _) -> None:
        if 'geo_tag_ids' not in errors:
            errors['geo_tag_ids'] = {}
        tag_index = str(error.context)
        if tag_index not in errors['geo_tag_ids']:
            errors['geo_tag_ids'][tag_index] = []
        errors['geo_tag_ids'][tag_index].append({'type': error.error_code, 'message': error.error_message})

    db_error_appender = BaseDBErrorAppender({
        ErrorCode.INVALID_PROVIDER_ID: append_invalid_provider_id_error,
        ErrorCode.INVALID_TAG_ID: append_invalid_tag_id_error,
        ErrorCode.INVALID_GEO_TAG_ID: append_invalid_geo_tag_id_error,
    })


class AddOpportunityTagFormatter(BaseSerializerFormatter, BaseDBFormatter):
    class ErrorCode(IntEnum):
        INVALID_OPPORTUNITY_ID = 200
        INVALID_TAG_ID = 201

    serializer_error_appender = RootSerializerErrorAppender (
        query=APISerializerErrorAppender(
            opportunity_id=append_serializer_field_error_factory(transform_id_error_factory('Opportunity id')),
        ).append_error,
        body=BaseSerializerErrorAppender(
            tag_ids=append_serializer_list_error_factory(
                transformer=transform_list_error_factory('Tag ids'),
                element_error_appender=append_serializer_field_error_factory(transform_id_error_factory('Tag id')),
            ),
        ).append_error,
    )

    @staticmethod
    def transform_invalid_opportunity_id_error(*_) -> FormattedError:
        return (AddOpportunityTagFormatter.ErrorCode.INVALID_OPPORTUNITY_ID,
                'Opportunity with provided id doesn\'t exist')

    @staticmethod
    def append_invalid_tag_id_error(error: GenericError[AddOpportunityTagErrorCode, int], errors: ErrorTrace, _) \
            -> None:
        if 'tag_ids' not in errors:
            errors['tag_ids'] = {}
        tag_index = str(error.context)
        if tag_index not in errors['tag_ids']:
            errors['tag_ids'][tag_index] = []
        errors['tag_ids'][tag_index].append({'type': AddOpportunityTagFormatter.ErrorCode.INVALID_TAG_ID,
                                             'message': 'Opportunity tag with provided id doesn\'t exist'})

    db_error_appender = BaseDBErrorAppender({
        AddOpportunityTagErrorCode.INVALID_OPPORTUNITY_ID:
            append_db_field_error_factory('opportunity_id', transformer=transform_invalid_opportunity_id_error),
        AddOpportunityTagErrorCode.INVALID_TAG_ID: append_invalid_tag_id_error,
    })

class AddOpportunityGeoTagFormatter(BaseSerializerFormatter, BaseDBFormatter):
    class ErrorCode(IntEnum):
        INVALID_OPPORTUNITY_ID = 200
        INVALID_GEO_TAG_ID = 201

    serializer_error_appender = RootSerializerErrorAppender(
        query=APISerializerErrorAppender(
            opportunity_id=append_serializer_field_error_factory(transform_id_error_factory('Opportunity id')),
        ).append_error,

        body=BaseSerializerErrorAppender(
            geo_tag_ids=append_serializer_list_error_factory(
                transformer=transform_list_error_factory('Geo tag ids'),
                element_error_appender=append_serializer_field_error_factory(transform_id_error_factory('Geo tag id')),
            ),
        ).append_error,
    )

    @staticmethod
    def transform_invalid_opportunity_id_error(*_) -> FormattedError:
        return (AddOpportunityGeoTagFormatter.ErrorCode.INVALID_OPPORTUNITY_ID,
                'Opportunity with provided id doesn\'t exist')

    @staticmethod
    def append_invalid_geo_tag_id_error(error: GenericError[AddOpportunityGeoTagErrorCode, int],
                                        errors: ErrorTrace, _) -> None:
        if 'geo_tag_ids' not in errors:
            errors['geo_tag_ids'] = {}
        tag_index = str(error.context)
        if tag_index not in errors['geo_tag_ids']:
            errors['geo_tag_ids'][tag_index] = []
        errors['geo_tag_ids'][tag_index].append({'type': AddOpportunityGeoTagFormatter.ErrorCode.INVALID_GEO_TAG_ID,
                                                 'message': 'Opportunity geo tag with provided id doesn\'t exist'})

    db_error_appender = BaseDBErrorAppender({
        AddOpportunityGeoTagErrorCode.INVALID_OPPORTUNITY_ID:
            append_db_field_error_factory('opportunity_id', transformer=transform_invalid_opportunity_id_error),
        AddOpportunityGeoTagErrorCode.INVALID_GEO_TAG_ID: append_invalid_geo_tag_id_error,
    })

class UpdateOpportunityDescriptionFormatter(BaseSerializerFormatter):
    @staticmethod
    def transform_description_error(error: PydanticError, _root: int) -> FormattedError | None:
        match error['type']:
            case 'missing':
                return FieldErrorCode.MISSING, 'Missing required field'
            case 'value_error':
                return FieldErrorCode.WRONG_TYPE, 'Description must be a file'

    serializer_error_appender = RootSerializerErrorAppender(
        query=APISerializerErrorAppender(
            opportunity_id=append_serializer_field_error_factory(transform_id_error_factory('Opportunity id')),
        ).append_error,
        body=BaseSerializerErrorAppender(
            description=append_serializer_field_error_factory(transform_description_error),
        ).append_error,
    )

    @staticmethod
    def get_invalid_content_type_error() -> ErrorTrace:
        return {
            'description': [{
                'type': FieldErrorCode.WRONG_TYPE,
                'message': 'Description must be a Markdown file',
            }]
        }
