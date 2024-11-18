from formatters.base import *
from models.opportunity.opportunity import CreateOpportunityCardErrorCode


class CreateOpportunityCardFormatter(BaseSerializerFormatter, BaseDBFormatter):
    class ErrorCode(IntEnum):
        INVALID_OPPORTUNITY_ID = 200

    serializer_error_appender = APISerializerErrorAppender(
        opportunity_id=append_serializer_field_error_factory(transform_id_error_factory('Opportunity id')),
        title=append_serializer_field_error_factory(transform_str_error_factory('Opportunity card title', min_length=1,
                                                                                max_length=30)),
        sub_title=append_serializer_field_error_factory(transform_str_error_factory('Opportunity card subtitle',
                                                                                    min_length=1, max_length=30)),
    )

    @staticmethod
    def transform_invalid_opportunity_id_error(*_) -> FormattedError:
        return (CreateOpportunityCardFormatter.ErrorCode.INVALID_OPPORTUNITY_ID,
                'Opportunity with provided id doesn\'t exist')

    db_error_appender = BaseDBErrorAppender({
        CreateOpportunityCardErrorCode.INVALID_OPPORTUNITY_ID:
            append_db_field_error_factory('opportunity_id', transformer=transform_invalid_opportunity_id_error),
    })
