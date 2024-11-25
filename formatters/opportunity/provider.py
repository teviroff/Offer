from dns.e164 import query

from formatters.base import *


class CreateProviderFormatter(BaseSerializerFormatter):
    # serializer_error_appender = APISerializerErrorAppender(
    #     name=append_serializer_field_error_factory(transform_str_error_factory('Provider name', min_length=4,
    #                                                                            max_length=50)),
    # )
    serializer_error_appender = RootSerializerErrorAppender(
        query=APISerializerErrorAppender().append_error,
        body=BaseSerializerErrorAppender(
            name=append_serializer_field_error_factory(transform_str_error_factory('Provider name',
                                                                                    min_length=4, max_length=50)),
        ).append_error
    )

