from formatters.base import *
from models.opportunity.opportunity import CreateOpportunityTagErrorCode


class CreateOpportunityTagFormatter(BaseSerializerFormatter, BaseDBFormatter):
    class ErrorCode(IntEnum):
        NON_UNIQUE_NAME = 200

    serializer_error_appender = RootSerializerErrorAppender(
        query=APISerializerErrorAppender().append_error,
        body=BaseSerializerErrorAppender(
            name=append_serializer_field_error_factory(transform_str_error_factory(
                'Opportunity tag name', min_length=1,)
            )
        ).append_error
    )

    @staticmethod
    def transform_non_unique_name_error(*_) -> FormattedError:
        return CreateOpportunityTagFormatter.ErrorCode.NON_UNIQUE_NAME, 'Tag with provided name already exists'

    db_error_appender = BaseDBErrorAppender({
        CreateOpportunityTagErrorCode.NON_UNIQUE_NAME:
            append_db_field_error_factory(field_name='name', transformer=transform_non_unique_name_error),
    })


class GetOpportunityTagByID:
    """Convenience class with DB error message."""

    @classmethod
    def create_db_error[T: IntEnum, C](cls, *, error_code: T, context: C) -> GenericError[T, C]:
        return GenericError(error_code, 'Opportunity tag with provided id doesn\'t exist', context=context)
