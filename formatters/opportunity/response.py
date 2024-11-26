from formatters.base import *


class CreateOpportunityResponseFormatter(BaseSerializerFormatter):
    class ErrorCode(IntEnum):
        OPPORTUNITY_NO_FORM = 201

    serializer_error_appender = BaseSerializerErrorAppender(
        opportunity_id=append_serializer_field_error_factory(transform_id_error_factory('Opportunity id')),
    )

    @staticmethod
    def get_missing_field_error() -> FormattedError:
        return FieldErrorCode.MISSING, 'Missing required field'

    @staticmethod
    def get_extra_field_error() -> FormattedError:
        return FieldErrorCode.EXTRA, 'Recieved extra field'

    @staticmethod
    def append_field_error(errors: ErrorTrace, *, field_name: str, error: FormattedError) -> None:
        field: list | None = errors.get(field_name)
        if field is None:
            errors[field_name] = [formatted_error_to_trace_entry(error)]
        else:
            field.append(formatted_error_to_trace_entry(error))

    @staticmethod
    def get_opportunity_no_form_error() -> ErrorTrace:
        return {
            'opportunity_id': [{
                'type': CreateOpportunityResponseFormatter.ErrorCode.OPPORTUNITY_NO_FORM,
                'message': 'Provided opportunity has no submit form'
            }]
        }
