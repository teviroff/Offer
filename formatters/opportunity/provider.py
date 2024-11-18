from formatters.base import *


class CreateProviderFormatter(BaseSerializerFormatter):
    serializer_error_appender = APISerializerErrorAppender(
        name=append_serializer_field_error_factory(transform_str_error_factory('Provider name', min_length=4,
                                                                               max_length=50)),
    )
