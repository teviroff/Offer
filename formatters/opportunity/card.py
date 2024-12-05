from formatters.base import *


class CreateOpportunityCardFormatter(BaseSerializerFormatter):
    serializer_error_appender = RootSerializerErrorAppender(
        query=APISerializerErrorAppender(
            opportunity_id=append_serializer_field_error_factory(transform_id_error_factory('Opportunity id')),
        ).append_error,
        body=BaseSerializerErrorAppender(
            title=append_serializer_field_error_factory(transform_str_error_factory('Card title',
                                                                                    min_length=1, max_length=30)),
            subtitle=append_serializer_field_error_factory(transform_str_error_factory('Card subtitle',
                                                                                       min_length=1, max_length=30)),
        ).append_error,
    )
