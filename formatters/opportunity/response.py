from formatters.base import *


class CreateOpportunityResponseFormatter(BaseSerializerFormatter):
    class ErrorCode(IntEnum):
        OPPORTUNITY_NO_FORM = 201
        ALREADY_RESPONDED = 202

    serializer_error_appender = BaseSerializerErrorAppender(
        opportunity_id=append_serializer_field_error_factory(transform_id_error_factory('Opportunity id')),
    )

    @staticmethod
    def get_opportunity_no_form_error() -> ErrorTrace:
        return {
            'opportunity_id': [{
                'type': CreateOpportunityResponseFormatter.ErrorCode.OPPORTUNITY_NO_FORM,
                'message': 'Provided opportunity has no submit form'
            }]
        }

    @staticmethod
    def get_already_responded_error() -> ErrorTrace:
        return {
            'user_id': [{
                'type': CreateOpportunityResponseFormatter.ErrorCode.ALREADY_RESPONDED,
                'message': 'User with provided id already submitted for this opportunity'
            }]
        }
