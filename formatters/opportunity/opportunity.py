from formatters.base import *
from utils import *
from models.opportunity.opportunity import (
    CreateOpportunityErrorCode, AddOpportunityTagErrorCode,
    AddOpportunityGeoTagErrorCode,
)


class CreateOpportunityFormatter(BaseSerializerFormatter, BaseDBFormatter):
    class ErrorCode(IntEnum):
        INVALID_PROVIDER_ID = 200

    serializer_error_appender = APISerializerErrorAppender(
        name=append_serializer_field_error_factory(
            field_name='name',
            transformer=transform_str_error_factory('Opportunity name', min_length=1, max_length=50)
        ),
        provider_id=append_serializer_field_error_factory(
            field_name='provider_id',
            transformer=transform_id_error_factory('Opportunity provider id')
        ),
        description=append_serializer_field_error_factory(
            field_name='description',
            transformer=transform_str_error_factory('Opportunity description', min_length=0, max_length=250)
        ),
    )

    @staticmethod
    def transform_invalid_provider_id_error(_) -> FormattedError:
        return CreateOpportunityFormatter.ErrorCode.INVALID_PROVIDER_ID, \
               'Opportunity provider with given id doesn\'t exist'

    db_error_appender = BaseDBErrorAppender({
        CreateOpportunityErrorCode.INVALID_PROVIDER_ID:
            append_db_field_error_factory('provider_id', transformer=transform_invalid_provider_id_error),
    })


class AddOpportunityTagFormatter(BaseSerializerFormatter, BaseDBFormatter):
    class ErrorCode(IntEnum):
        INVALID_OPPORTUNITY_ID = 200
        INVALID_TAG_ID = 201

    serializer_error_appender = APISerializerErrorAppender(
        opportunity_id=append_serializer_field_error_factory(
            field_name='opportunity_id',
            transformer=transform_id_error_factory('Opportunity id')
        ),
        tag_ids=append_serializer_list_error_factory(
            list_field_name='tag_ids',
            transformer=transform_list_error_factory('Tag ids'),
            element_transformer=transform_id_error_factory('Tag id')
        ),
    )

    @staticmethod
    def transform_invalid_opportunity_id_error(_) -> FormattedError:
        return (AddOpportunityTagFormatter.ErrorCode.INVALID_OPPORTUNITY_ID,
                'Opportunity with provided id doesn\'t exist')

    @staticmethod
    def append_invalid_tag_id_error(error: GenericError[AddOpportunityTagErrorCode, int], errors: Result) -> None:
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

    serializer_error_appender = APISerializerErrorAppender(
        opportunity_id=append_serializer_field_error_factory(
            field_name='opportunity_id',
            transformer=transform_id_error_factory('Opportunity id')
        ),
        geo_tag_ids=append_serializer_list_error_factory(
            list_field_name='geo_tag_ids',
            transformer=transform_list_error_factory('Geo tag ids'),
            element_transformer=transform_id_error_factory('Geo tag id')
        ),
    )

    @staticmethod
    def transform_invalid_opportunity_id_error(_) -> FormattedError:
        return (AddOpportunityGeoTagFormatter.ErrorCode.INVALID_OPPORTUNITY_ID,
                'Opportunity with provided id doesn\'t exist')

    @staticmethod
    def append_invalid_geo_tag_id_error(error: GenericError[AddOpportunityGeoTagErrorCode, int], errors: Result) \
            -> None:
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
