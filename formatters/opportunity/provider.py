from formatters.base import *


class CreateProviderFormatter(BaseSerializerFormatter):
    serializer_error_appender = RootSerializerErrorAppender(
        query=APISerializerErrorAppender().append_error,
        body=BaseSerializerErrorAppender(
            name=append_serializer_field_error_factory(transform_str_error_factory('Provider name',
                                                                                   min_length=4, max_length=50)),
        ).append_error
    )

class GetOpportunityProviderByID:
    """Convenience class with DB error message."""

    @classmethod
    def create_db_error[T: IntEnum, C](cls, *, error_code: T, context: C) -> GenericError[T, C]:
        return GenericError(error_code, 'Opportunity provider with provided id doesn\'t exist', context=context)
