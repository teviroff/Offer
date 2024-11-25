from formatters.base import *
from models.opportunity.opportunity import CreateOpportunityGeoTagErrorCode


class CreateOpportunityGeoTagFormatter(BaseSerializerFormatter, BaseDBFormatter):
    class ErrorCode(IntEnum):
        INVALID_CITY_ID = 200
        NON_UNIQUE_CITY = 201

    serializer_error_appender = APISerializerErrorAppender(
        city_id=append_serializer_field_error_factory(transform_id_error_factory('City id')),
    )

    @staticmethod
    def transform_invalid_city_id_error(*_) -> FormattedError:
        return CreateOpportunityGeoTagFormatter.ErrorCode.INVALID_CITY_ID, 'City with provided id doesn\'t exist'

    @staticmethod
    def transform_non_unique_city_error(*_) -> FormattedError:
        return (CreateOpportunityGeoTagFormatter.ErrorCode.NON_UNIQUE_CITY,
                'Geo tag with provided city id already exists')

    db_error_appender = BaseDBErrorAppender({
        CreateOpportunityGeoTagErrorCode.INVALID_CITY_ID:
            append_db_field_error_factory(field_name='city_id', transformer=transform_invalid_city_id_error),
        CreateOpportunityGeoTagErrorCode.NON_UNIQUE_CITY:
            append_db_field_error_factory(field_name='city_id', transformer=transform_non_unique_city_error),
    })
